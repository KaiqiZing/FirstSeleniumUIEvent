# -*- coding: utf-8 -*-
"""结算单父子级金额接口：父级结算单 + 子级明细，模拟金额勾稽、尾差与后台重算。"""
import copy
import threading
import time

from flask import Blueprint, jsonify, request

from config import Config

bp = Blueprint("settlement_api", __name__)

_lock = threading.Lock()


def _round2(v):
    return round(float(v), 2)


def _build_parents():
    """构造三张父单：一条金额一致、一条存在一分钱尾差、一条含负数冲销明细。"""
    return [
        {
            "id": "S-20260915-001",
            "customer": "启元资产管理有限公司",
            "bizType": "场内交易结算",
            "settleDate": "2026-09-15",
            "declaredAmount": 1286500.00,
            "children": [
                {"id": "D-0001", "name": "股票买入交割", "subject": "证券清算款", "amount": 862300.00},
                {"id": "D-0002", "name": "交易佣金", "subject": "手续费及佣金", "amount": 3680.50},
                {"id": "D-0003", "name": "印花税", "subject": "税金及附加", "amount": 1286.50},
                {"id": "D-0004", "name": "过户费", "subject": "结算费用", "amount": 233.00},
                {"id": "D-0005", "name": "结算备付金退回", "subject": "内部往来", "amount": 419000.00},
            ],
        },
        {
            "id": "S-20260915-002",
            "customer": "恒信证券自营账户",
            "bizType": "场外协议回购",
            "settleDate": "2026-09-15",
            "declaredAmount": 510710.99,
            "children": [
                {"id": "D-0011", "name": "回购本金", "subject": "买入返售金融资产", "amount": 512000.00},
                {"id": "D-0012", "name": "回购利息收入", "subject": "利息收入", "amount": 1250.30},
                {"id": "D-0013", "name": "结算费", "subject": "结算费用", "amount": 860.70},
                {"id": "D-0014", "name": "利息调整冲销", "subject": "利息调整", "amount": -3400.00},
            ],
        },
        {
            "id": "S-20260915-003",
            "customer": "南方稳健混合型基金",
            "bizType": "基金申赎结算",
            "settleDate": "2026-09-16",
            "declaredAmount": 304800.00,
            "children": [
                {"id": "D-0021", "name": "基金申购款", "subject": "应收申购款", "amount": 300000.00},
                {"id": "D-0022", "name": "申购手续费", "subject": "手续费及佣金", "amount": 4800.00},
            ],
        },
    ]


_parents = _build_parents()


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "data": data, "message": message})


def fail(message, code=1):
    return jsonify({"code": code, "data": None, "message": message})


def _summarize(parent):
    """按子单金额重算父单勾稽结果；保留浮点原始合计用于演示尾差。"""
    amounts = [float(c["amount"]) for c in parent["children"]]
    raw_total = sum(amounts)  # 浮点直接相加，可能出现 0.0000000x 尾差
    child_total = _round2(raw_total)
    declared = _round2(parent["declaredAmount"])
    diff = _round2(child_total - declared)
    return {
        "parentId": parent["id"],
        "declaredAmount": declared,
        "childTotal": child_total,
        "rawChildTotal": raw_total,
        "diff": diff,
        "state": "matched" if abs(diff) < 0.005 else "diff",
    }


@bp.get("/settlement/list")
def settlement_list():
    """返回父级结算单及其子级明细（子级由前端默认折叠，不渲染到 DOM）。"""
    with _lock:
        snapshot = copy.deepcopy(_parents)
    for p in snapshot:
        p.update(_summarize(p))
    return ok({"parents": snapshot})


@bp.post("/settlement/recalc")
def settlement_recalc():
    """子单金额变更后重算父单勾稽：sleep 模拟后台清算处理，父单金额异步刷新。"""
    payload = request.get_json(silent=True) or {}
    parent_id = (payload.get("parentId") or "").strip()
    items = payload.get("items") or []

    with _lock:
        parent = next((p for p in _parents if p["id"] == parent_id), None)
        if not parent:
            return fail("结算单不存在: %s" % parent_id)
        for item in items:
            try:
                amount = _round2(item.get("amount"))
            except (TypeError, ValueError):
                continue
            child = next((c for c in parent["children"] if c["id"] == item.get("id")), None)
            if child:
                child["amount"] = amount
        result = _summarize(parent)

    time.sleep(Config.SETTLEMENT_RECALC_DELAY)
    return ok(result)


@bp.post("/settlement/reset")
def settlement_reset():
    """重置为初始结算数据，保证练习可重复。"""
    global _parents
    with _lock:
        _parents = _build_parents()
    return ok({"reset": True})
