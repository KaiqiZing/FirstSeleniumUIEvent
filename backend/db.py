# -*- coding: utf-8 -*-
"""SQLite 数据层：为「页面数字 与 数据库一致性核对」场景提供可直连查询的真实落库。

设计要点（均为金融系统常见现状，非缺陷，需由自动化脚本自行处理）：
1. 金额一律以「分」(INTEGER) 落库，页面按「元」展示 —— 单位不一致。
2. settle_bill.total_amount_cents 是独立存储的汇总字段，与明细求和可能不等（本数据里 002 差 1 分）。
3. 存在未清算明细，amount_cents 为 NULL，页面展示为「—」。
4. 数据库文件位于 backend/data/settlement.db，可用 sqlite3 / DBeaver 直接打开核对。
"""
import os
import sqlite3
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "settlement.db")

_lock = threading.Lock()

# (bill_no, customer, biz_type, settle_date, total_amount_cents, status, updated_at)
_INITIAL_BILLS = [
    ("S-20260915-001", "启元资产管理有限公司", "场内交易结算", "2026-09-15", 128650000, "settled", "2026-09-15 17:20:03"),
    # 汇总字段比明细求和多 1 分（明细和为 48011100）：模拟汇总表与明细表漂移
    ("S-20260915-002", "恒信证券自营账户", "场外协议回购", "2026-09-15", 48011101, "settled", "2026-09-15 17:22:41"),
    ("S-20260915-003", "南方稳健混合型基金", "基金申赎结算", "2026-09-16", 30480000, "partial", "2026-09-16 09:05:12"),
    ("S-20260915-004", "天元量化三号私募", "融资融券结算", "2026-09-16", 5286250, "settled", "2026-09-16 09:11:30"),
]

# (bill_no, item_no, item_name, subject, amount_cents, updated_at)
_INITIAL_DETAILS = [
    ("S-20260915-001", "D-0001", "股票买入交割", "证券清算款", 86230000, "2026-09-15 17:20:03"),
    ("S-20260915-001", "D-0002", "交易佣金", "手续费及佣金", 368050, "2026-09-15 17:20:03"),
    ("S-20260915-001", "D-0003", "印花税", "税金及附加", 128650, "2026-09-15 17:20:03"),
    ("S-20260915-001", "D-0004", "过户费", "结算费用", 23300, "2026-09-15 17:20:03"),
    ("S-20260915-001", "D-0005", "结算备付金退回", "内部往来", 41900000, "2026-09-15 17:20:03"),
    ("S-20260915-002", "D-0011", "回购本金", "买入返售金融资产", 51200000, "2026-09-15 17:22:41"),
    ("S-20260915-002", "D-0012", "回购利息收入", "利息收入", 125030, "2026-09-15 17:22:41"),
    ("S-20260915-002", "D-0013", "结算费", "结算费用", 86070, "2026-09-15 17:22:41"),
    ("S-20260915-002", "D-0014", "利息调整冲销", "利息调整", -3400000, "2026-09-15 17:22:41"),
    ("S-20260915-003", "D-0021", "基金申购款", "应收申购款", 30000000, "2026-09-16 09:05:12"),
    ("S-20260915-003", "D-0022", "申购手续费", "手续费及佣金", 480000, "2026-09-16 09:05:12"),
    # 未清算：库中为 NULL，页面展示为「—」
    ("S-20260915-003", "D-0023", "赎回款", "应付赎回款", None, "2026-09-16 09:05:12"),
    ("S-20260915-004", "D-0031", "融资买入本金", "融出资金", 15000000, "2026-09-16 09:11:30"),
    ("S-20260915-004", "D-0032", "融资利息", "利息收入", 86250, "2026-09-16 09:11:30"),
    ("S-20260915-004", "D-0033", "融券卖出所得", "融出证券", -9800000, "2026-09-16 09:11:30"),
]

# (account_no, customer_name, available_cents, frozen_cents, updated_at)
_INITIAL_ACCOUNTS = [
    ("10000088", "启元资产管理有限公司", 386520000, 12000000, "2026-09-16 09:00:00"),
    ("10000126", "恒信证券自营账户", 95230000, 0, "2026-09-16 09:00:00"),
    ("10000233", "南方稳健混合型基金", 20480000, 4500000, "2026-09-16 09:00:00"),
    ("10000455", "天元量化三号私募", 7865000, 1250000, "2026-09-16 09:00:00"),
]


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def connect():
    """每次调用新建连接：Flask 以 threaded 模式运行，连接不跨线程复用。"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def _create_tables(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS settle_bill (
            bill_no            TEXT PRIMARY KEY,
            customer           TEXT NOT NULL,
            biz_type           TEXT NOT NULL,
            settle_date        TEXT NOT NULL,
            total_amount_cents INTEGER NOT NULL,
            status             TEXT NOT NULL,
            updated_at         TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS settle_detail (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no      TEXT NOT NULL,
            item_no      TEXT NOT NULL,
            item_name    TEXT NOT NULL,
            subject      TEXT NOT NULL,
            amount_cents INTEGER,
            updated_at   TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fund_account (
            account_no      TEXT PRIMARY KEY,
            customer_name   TEXT NOT NULL,
            available_cents INTEGER NOT NULL,
            frozen_cents    INTEGER NOT NULL,
            updated_at      TEXT NOT NULL
        );
        """
    )


def _seed(conn):
    conn.executemany(
        "INSERT OR REPLACE INTO settle_bill VALUES (?,?,?,?,?,?,?)", _INITIAL_BILLS
    )
    conn.executemany(
        "INSERT INTO settle_detail (bill_no,item_no,item_name,subject,amount_cents,updated_at) VALUES (?,?,?,?,?,?)",
        _INITIAL_DETAILS,
    )
    conn.executemany(
        "INSERT OR REPLACE INTO fund_account VALUES (?,?,?,?,?)", _INITIAL_ACCOUNTS
    )


def init_db():
    """应用启动时建库建表；仅在明细表为空时灌入初始数据。"""
    with _lock:
        conn = connect()
        try:
            _create_tables(conn)
            count = conn.execute("SELECT COUNT(*) c FROM settle_detail").fetchone()["c"]
            if count == 0:
                _seed(conn)
            conn.commit()
        finally:
            conn.close()


def reset_db():
    """删表重建并灌回初始数据，保证练习可重复。"""
    with _lock:
        conn = connect()
        try:
            conn.executescript(
                "DROP TABLE IF EXISTS settle_detail;"
                "DROP TABLE IF EXISTS settle_bill;"
                "DROP TABLE IF EXISTS fund_account;"
            )
            _create_tables(conn)
            _seed(conn)
            conn.commit()
        finally:
            conn.close()


def to_yuan(cents):
    """分 -> 元；NULL 原样返回 None（页面需显式处理未清算）。"""
    if cents is None:
        return None
    return round(int(cents) / 100.0, 2)


def to_cents(yuan):
    """元 -> 分；用四舍五入避免浮点误差放大。"""
    return int(round(float(yuan) * 100))
