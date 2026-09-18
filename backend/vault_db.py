# -*- coding: utf-8 -*-
"""密文库：为「页面数字 与 密文存储核对」场景提供真实的落库密文。

与 settlement.db 的区别：本库中所有敏感字段（手机号 / 证件号 / 余额）一律以 AES-256-GCM 密文落库，
页面看到的是服务端解密后的明文，二者不可直接肉眼对照。

刻意保留的现状（均需自动化脚本自行识别处理）：
1. 相同明文两次加密得到的密文不同（IV 随机）→ 不能用密文字符串做相等断言。
2. 存在历史密钥版本 K1 → 用默认（当前）密钥解密会失败。
3. 存在已吊销版本 K0（密钥已销毁）→ 永久解不开，页面显示「解密失败」。
4. 存在未登记字段，库中为 NULL，需与「解密失败」区分对待。
5. 无法加密检索 → 另建 HMAC 摘要列做密文字段的等值查询。
"""
import os
import sqlite3
import threading
import time

import crypto_util as cu

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "crypto_vault.db")

_lock = threading.Lock()

# (cust_no, cust_name, mobile, idcard, balance, key_version, note)
_INITIAL_ROWS = [
    ("C-1001", "启元资产管理有限公司", "13812348000", "310101199203078123", "862300.00", "K2", "常规客户"),
    ("C-1002", "恒信证券自营账户", "13905718888", "310101198811224517", "512000.00", "K2", "常规客户"),
    ("C-1003", "南方稳健混合型基金", "13600129876", "440301199507113326", "304800.00", "K2", "常规客户"),
    # 未登记结算余额：库中为 NULL，页面展示「—」
    ("C-1004", "天元量化三号私募", "15021097788", "120103198209054411", None, "K2", "未登记结算余额"),
    # 历史密钥版本：必须用 K1 密钥才能解开，用默认当前密钥解密会失败
    ("C-1005", "星海信托单一计划", "13712346688", "110105199309126657", "98650.00", "K1", "密钥轮换前落库"),
    # 已吊销版本：密钥已销毁，任何情况下都解不开
    ("C-1006", "云帆稳健 FOF 一号", "13566778899", None, "125030.00", "K0", "密钥已吊销待重加密"),
]


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _encrypt_triple(mobile, idcard, balance, version):
    """把三个明文字段加密成 (密文, iv) 三元组；明文为 None 时保持 NULL。"""
    out = {}
    for field, plain in (("mobile", mobile), ("idcard", idcard), ("balance", balance)):
        if plain is None:
            out[field + "_enc"] = None
            out[field + "_iv"] = None
        else:
            box = cu.aes_encrypt(plain, version) if version in ("K1", "K2") else {
                "cipherB64": cu.b64e(os.urandom(48)),
                "ivB64": cu.b64e(os.urandom(12)),
            }
            out[field + "_enc"] = box["cipherB64"]
            out[field + "_iv"] = box["ivB64"]
    return out


def _ensure_schema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cust_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cust_no TEXT NOT NULL,
            cust_name TEXT NOT NULL,
            mobile_enc TEXT, mobile_iv TEXT, mobile_hmac TEXT,
            idcard_enc TEXT, idcard_iv TEXT,
            balance_enc TEXT, balance_iv TEXT,
            key_version TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            note TEXT
        )
        """
    )
    conn.commit()


def _seed(conn):
    ts = now()
    for no, name, mobile, idcard, balance, version, note in _INITIAL_ROWS:
        box = _encrypt_triple(mobile, idcard, balance, version)
        conn.execute(
            """
            INSERT INTO cust_profile
              (cust_no, cust_name, mobile_enc, mobile_iv, mobile_hmac,
               idcard_enc, idcard_iv, balance_enc, balance_iv, key_version, updated_at, note)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                no, name,
                box["mobile_enc"], box["mobile_iv"],
                cu.indexed_hmac(mobile) if mobile else None,
                box["idcard_enc"], box["idcard_iv"],
                box["balance_enc"], box["balance_iv"],
                version, ts, note,
            ),
        )
    conn.commit()


def init_vault():
    """启动时重建密文库：密钥随进程生成，跨进程的旧密文必然解不开，
    因此每次启动都用当前密钥重新灌一遍初始数据（与其他场景「内存态、重启即复原」一致）。"""
    reset_vault()


def reset_vault():
    """重建密文库：由于密钥在进程启动时随机生成，旧密文将永久无法解开，必须整体重建。"""
    with _lock:
        conn = _connect()
        try:
            conn.execute("DROP TABLE IF EXISTS cust_profile")
            _ensure_schema(conn)
            _seed(conn)
        finally:
            conn.close()


def count_rows():
    with _lock:
        conn = _connect()
        try:
            return conn.execute("SELECT COUNT(1) AS c FROM cust_profile").fetchone()["c"]
        finally:
            conn.close()


def raw_rows():
    """库表原始行：密文、IV、摘要与密钥版本，不带任何解密。"""
    with _lock:
        conn = _connect()
        try:
            rows = conn.execute(
                """
                SELECT id, cust_no, cust_name, mobile_enc, mobile_iv, mobile_hmac,
                       idcard_enc, idcard_iv, balance_enc, balance_iv,
                       key_version, updated_at, note
                FROM cust_profile ORDER BY id
                """
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


def meta():
    with _lock:
        conn = _connect()
        try:
            total = conn.execute("SELECT COUNT(1) AS c FROM cust_profile").fetchone()["c"]
            last = conn.execute("SELECT MAX(updated_at) AS t FROM cust_profile").fetchone()["t"]
            versions = conn.execute(
                "SELECT key_version AS v, COUNT(1) AS c FROM cust_profile GROUP BY key_version ORDER BY key_version"
            ).fetchall()
        finally:
            conn.close()
    return {
        "dbPath": DB_PATH,
        "table": "cust_profile",
        "rows": total,
        "lastUpdatedAt": last,
        "keyVersions": [{"version": r["v"], "count": r["c"]} for r in versions],
        "currentKeyVersion": cu.CURRENT_KEY_VERSION,
        "alg": "AES-256-GCM",
    }


def insert_profile(cust_no, cust_name, mobile, idcard, balance):
    """新登记一条档案：明文入库前加密，同一明文再次写入会得到完全不同的密文。"""
    box = _encrypt_triple(mobile, idcard, balance, cu.CURRENT_KEY_VERSION)
    ts = now()
    with _lock:
        conn = _connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO cust_profile
                  (cust_no, cust_name, mobile_enc, mobile_iv, mobile_hmac,
                   idcard_enc, idcard_iv, balance_enc, balance_iv, key_version, updated_at, note)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    cust_no, cust_name,
                    box["mobile_enc"], box["mobile_iv"],
                    cu.indexed_hmac(mobile) if mobile else None,
                    box["idcard_enc"], box["idcard_iv"],
                    box["balance_enc"], box["balance_iv"],
                    cu.CURRENT_KEY_VERSION, ts, "本次会话新增",
                ),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()
