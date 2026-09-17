# -*- coding: utf-8 -*-
"""页面数字 与 数据库 一致性核对接口：真实落库（SQLite），并提供直连查询入口。

页面侧拿到的是「元、格式化、分页、汇总字段」，
数据库侧是「分、全量、含 NULL」，两者天然存在需要脚本自行换算与对齐的差异。
"""
import time

from flask import Blueprint, jsonify, request

import db
from config import Config

bp = Blueprint("dbconsistency_api", __name__)


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "data": data, "message": message})


def fail(message, code=1):
    return jsonify({"code": code, "data": None, "message": message})


def _dicts(rows):
    return [dict(r) for r in rows]


# ---------------------------------------------------------------- 页面数据源


@bp.get("/dbconsistency/page")
def page():
    """页面列表数据：明细分页 + 汇总卡片（汇总卡片来自独立字段，非明细实时求和）。"""
    page_no = max(1, int(request.args.get("page") or 1))
    size = max(1, int(request.args.get("size") or Config.DB_PAGE_SIZE))

    conn = db.connect()
    try:
        total = conn.execute("SELECT COUNT(*) c FROM settle_detail").fetchone()["c"]
        offset = (page_no - 1) * size
        rows = conn.execute(
            """
            SELECT d.id, d.bill_no, d.item_no, d.item_name, d.subject,
                   d.amount_cents, d.updated_at, b.total_amount_cents AS bill_total_cents
            FROM settle_detail d
            LEFT JOIN settle_bill b ON b.bill_no = d.bill_no
            ORDER BY d.id
            LIMIT ? OFFSET ?
            """,
            (size, offset),
        ).fetchall()

        bill_sum = conn.execute(
            "SELECT COALESCE(SUM(total_amount_cents),0) s FROM settle_bill"
        ).fetchone()["s"]
        detail_sum = conn.execute(
            "SELECT COALESCE(SUM(amount_cents),0) s FROM settle_detail"
        ).fetchone()["s"]
        available = conn.execute(
            "SELECT COALESCE(SUM(available_cents),0) s FROM fund_account"
        ).fetchone()["s"]
        frozen = conn.execute(
            "SELECT COALESCE(SUM(frozen_cents),0) s FROM fund_account"
        ).fetchone()["s"]
        accounts = conn.execute(
            "SELECT account_no, customer_name, available_cents, frozen_cents, updated_at"
            " FROM fund_account ORDER BY account_no"
        ).fetchall()
    finally:
        conn.close()

    return ok(
        {
            "page": page_no,
            "size": size,
            "total": total,
            "rows": [
                {
                    "id": r["id"],
                    "billNo": r["bill_no"],
                    "itemNo": r["item_no"],
                    "itemName": r["item_name"],
                    "subject": r["subject"],
                    "amount": db.to_yuan(r["amount_cents"]),
                    "billTotal": db.to_yuan(r["bill_total_cents"]),
                    "updatedAt": r["updated_at"],
                }
                for r in rows
            ],
            "summary": {
                # 汇总字段求和（页面顶部结算单总额），与明细求和不一定相等
                "billTotalSum": db.to_yuan(bill_sum),
                # 数据库全量明细求和（页面不展示，供脚本核对）
                "detailSum": db.to_yuan(detail_sum),
                "detailCount": total,
                "accountAvailable": db.to_yuan(available),
                "accountFrozen": db.to_yuan(frozen),
                "snapshotAt": db.now(),
            },
            "accounts": [
                {
                    "accountNo": a["account_no"],
                    "customerName": a["customer_name"],
                    "available": db.to_yuan(a["available_cents"]),
                    "frozen": db.to_yuan(a["frozen_cents"]),
                    "updatedAt": a["updated_at"],
                }
                for a in accounts
            ],
        }
    )


# ---------------------------------------------------------------- 数据库直查


@bp.get("/dbconsistency/db/meta")
def db_meta():
    """库文件路径与各表行数/最后更新时间，用于确定该查哪张表。"""
    conn = db.connect()
    try:
        tables = []
        for name in ("settle_bill", "settle_detail", "fund_account"):
            row = conn.execute(
                "SELECT COUNT(*) c, MAX(updated_at) t FROM %s" % name
            ).fetchone()
            tables.append({"table": name, "rows": row["c"], "updatedAt": row["t"]})
    finally:
        conn.close()
    return ok({"dbPath": db.DB_PATH, "tables": tables, "serverTime": db.now()})


@bp.get("/dbconsistency/db/query")
def db_query():
    """模拟直连数据库查询：返回原始行（金额为「分」，NULL 保持 null）。"""
    target = (request.args.get("target") or "settle_detail").strip()
    conn = db.connect()
    try:
        if target == "settle_bill":
            sql = "SELECT * FROM settle_bill"
            params = ()
            bill_no = request.args.get("billNo")
            if bill_no:
                sql += " WHERE bill_no = ?"
                params = (bill_no,)
        elif target == "fund_account":
            sql = "SELECT * FROM fund_account"
            params = ()
            account_no = request.args.get("accountNo")
            if account_no:
                sql += " WHERE account_no = ?"
                params = (account_no,)
        elif target == "settle_detail":
            sql = "SELECT * FROM settle_detail"
            params = ()
            bill_no = request.args.get("billNo")
            if bill_no:
                sql += " WHERE bill_no = ?"
                params = (bill_no,)
            sql += " ORDER BY id"
        else:
            return fail("未知表: %s" % target)
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    return ok({"table": target, "count": len(rows), "rows": _dicts(rows)})


# ---------------------------------------------------------------- 写操作


@bp.post("/dbconsistency/detail/update")
def detail_update():
    """调整明细金额：只写明细表，不回写结算单汇总字段（制造汇总与明细漂移）。"""
    payload = request.get_json(silent=True) or {}
    detail_id = payload.get("id")
    amount = payload.get("amount")
    try:
        cents = db.to_cents(amount)
    except (TypeError, ValueError):
        return fail("金额格式不正确")

    conn = db.connect()
    try:
        row = conn.execute(
            "SELECT id, bill_no FROM settle_detail WHERE id = ?", (detail_id,)
        ).fetchone()
        if not row:
            return fail("明细不存在: %s" % detail_id)
        conn.execute(
            "UPDATE settle_detail SET amount_cents = ?, updated_at = ? WHERE id = ?",
            (cents, db.now(), detail_id),
        )
        conn.commit()
        bill = conn.execute(
            "SELECT bill_no, total_amount_cents FROM settle_bill WHERE bill_no = ?",
            (row["bill_no"],),
        ).fetchone()
        detail_sum = conn.execute(
            "SELECT COALESCE(SUM(amount_cents),0) s FROM settle_detail WHERE bill_no = ?",
            (row["bill_no"],),
        ).fetchone()["s"]
    finally:
        conn.close()

    time.sleep(Config.DB_WRITE_DELAY)
    return ok(
        {
            "id": detail_id,
            "billNo": bill["bill_no"],
            "amount": db.to_yuan(cents),
            "billTotal": db.to_yuan(bill["total_amount_cents"]),
            "detailSum": db.to_yuan(detail_sum),
        }
    )


@bp.post("/dbconsistency/bill/recap")
def bill_recap():
    """按明细求和回写结算单汇总字段（把漂移修回来）。"""
    payload = request.get_json(silent=True) or {}
    bill_no = (payload.get("billNo") or "").strip()
    if not bill_no:
        return fail("billNo 不能为空")

    conn = db.connect()
    try:
        exists = conn.execute(
            "SELECT 1 FROM settle_bill WHERE bill_no = ?", (bill_no,)
        ).fetchone()
        if not exists:
            return fail("结算单不存在: %s" % bill_no)
        total = conn.execute(
            "SELECT COALESCE(SUM(amount_cents),0) s FROM settle_detail WHERE bill_no = ?",
            (bill_no,),
        ).fetchone()["s"]
        conn.execute(
            "UPDATE settle_bill SET total_amount_cents = ?, updated_at = ? WHERE bill_no = ?",
            (total, db.now(), bill_no),
        )
        conn.commit()
    finally:
        conn.close()

    time.sleep(Config.DB_WRITE_DELAY)
    return ok({"billNo": bill_no, "billTotal": db.to_yuan(total)})


@bp.post("/dbconsistency/account/post")
def account_post():
    """模拟清算入账：直接改数据库，页面不刷新即出现「页面数字 vs 数据库」不一致。"""
    payload = request.get_json(silent=True) or {}
    account_no = (payload.get("accountNo") or "").strip() or Config.DB_POST_ACCOUNT
    try:
        delta = db.to_cents(payload.get("delta", Config.DB_POST_DELTA_YUAN))
    except (TypeError, ValueError):
        return fail("入账金额格式不正确")

    conn = db.connect()
    try:
        row = conn.execute(
            "SELECT account_no, available_cents FROM fund_account WHERE account_no = ?",
            (account_no,),
        ).fetchone()
        if not row:
            return fail("资金账号不存在: %s" % account_no)
        new_value = int(row["available_cents"]) + delta
        conn.execute(
            "UPDATE fund_account SET available_cents = ?, updated_at = ? WHERE account_no = ?",
            (new_value, db.now(), account_no),
        )
        conn.commit()
    finally:
        conn.close()

    return ok(
        {
            "accountNo": account_no,
            "delta": db.to_yuan(delta),
            "available": db.to_yuan(new_value),
            "updatedAt": db.now(),
        }
    )


@bp.post("/dbconsistency/reset")
def reset():
    """重建数据库，恢复初始数据。"""
    db.reset_db()
    return ok({"reset": True})
