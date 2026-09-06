# -*- coding: utf-8 -*-
"""慢接口 / 不稳定接口 / 分页造数 / 自造自销数据接口。"""
import random
import threading
import time

from flask import Blueprint, jsonify, request

from config import Config

bp = Blueprint("slow_api", __name__)

_lock = threading.Lock()
_seed_counter = [0]
_seed_records = []

_STATUS_CYCLE = ["进行中", "已完成", "已暂停", "待审阅"]
_NAME_POOL = [
    "华北-经销商", "华东-直营店", "华南-加盟店", "西南-分销商",
    "西北-旗舰店", "东北-专营店", "华中-体验店", "海外-代理",
]

_PAGER_ROWS = []
for _i in range(1, Config.PAGER_TOTAL + 1):
    _PAGER_ROWS.append(
        {
            "id": "TASK-%04d" % _i,
            "name": "%s-任务%04d" % (_NAME_POOL[_i % len(_NAME_POOL)], _i),
            "owner": "工号%04d" % (_i * 7 % 9000 + 1000),
            "status": _STATUS_CYCLE[_i % len(_STATUS_CYCLE)],
            "amount": round(random.uniform(100, 9999), 2),
        }
    )


def _now():
    return time.strftime("%H:%M:%S")


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "data": data, "message": message})


def fail(message, data=None, code=1):
    return jsonify({"code": code, "data": data, "message": message})


@bp.get("/slow/items")
def slow_items():
    """模拟响应很慢的数据查询：sleep 后返回一批行。"""
    try:
        delay = float(request.args.get("delay", Config.SLOW_API_DEFAULT_DELAY))
    except ValueError:
        delay = Config.SLOW_API_DEFAULT_DELAY
    delay = min(max(delay, 0), 15)
    time.sleep(delay)

    rows = [
        {
            "id": "D%03d" % (i + 1),
            "name": "%s-%d" % (random.choice(_NAME_POOL), random.randint(1000, 9999)),
            "owner": "工号%04d" % random.randint(1000, 9999),
            "status": random.choice(_STATUS_CYCLE),
            "updated": _now(),
        }
        for i in range(Config.SLOW_ROWS)
    ]
    return ok({"rows": rows, "elapsed": "%.2f s" % delay})


@bp.get("/unstable")
def unstable():
    """不稳定接口：一定概率直接 500，其余随机 0.5~5s 后成功。"""
    if random.random() < Config.UNSTABLE_FAIL_RATE:
        return fail("服务暂时不可用，请稍后重试", code=500), 500
    low, high = Config.UNSTABLE_DELAY_RANGE
    time.sleep(random.uniform(low, high))
    size = random.randint(3, 10)
    rows = [
        {
            "id": "U%03d" % (i + 1),
            "name": random.choice(_NAME_POOL),
            "created": _now(),
        }
        for i in range(size)
    ]
    return ok({"rows": rows})


@bp.post("/upload")
def upload_file():
    """示例上传：仅登记文件名与大小（演示文件选择与回显）。"""
    f = request.files.get("file")
    if not f or not f.filename:
        return fail("未收到文件"), 400
    size = 0
    while True:
        chunk = f.stream.read(65536)
        if not chunk:
            break
        size += len(chunk)
    reg_no = "UP-%s-%03d" % (
        time.strftime("%Y%m%d%H%M%S"),
        random.randint(1, 999),
    )
    return ok({"filename": f.filename, "size": size, "regNo": reg_no})


@bp.get("/items")
def paged_items():
    """分页造数接口（滚动懒加载使用）。"""
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", Config.PAGER_PAGE_SIZE))
    except ValueError:
        page, size = 1, Config.PAGER_PAGE_SIZE
    size = min(max(size, 1), 50)
    page = max(page, 1)

    total = len(_PAGER_ROWS)
    start = (page - 1) * size
    end = start + size
    rows = _PAGER_ROWS[start:end]
    return ok(
        {
            "list": rows,
            "page": page,
            "size": size,
            "total": total,
            "hasMore": end < total,
        }
    )


@bp.post("/seed/new")
def seed_new():
    """自造自销：生成一条带时间戳后缀的唯一业务数据。"""
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "临时工单").strip()[:20]
    with _lock:
        _seed_counter[0] += 1
        seq = _seed_counter[0]
        record = {
            "id": "SEED-%s-%03d" % (time.strftime("%Y%m%d%H%M%S"), seq),
            "name": "%s-%s" % (name, time.strftime("%H%M%S%f")[:-3]),
            "created": _now(),
        }
        _seed_records.append(record)
    return ok(record)


@bp.get("/seed/list")
def seed_list():
    with _lock:
        return ok({"records": list(_seed_records)})


# ---- 竞态演示：保存耗时 2.6s，保存完成后数据才入库 ----
_race_store = []


@bp.post("/race/save")
def race_save():
    payload = request.get_json(silent=True) or {}
    remark = (payload.get("remark") or "未填写备注").strip()[:30]
    time.sleep(2.6)  # 模拟后端较长的落库处理
    with _lock:
        rec = {
            "id": "SV-%s-%03d" % (time.strftime("%Y%m%d%H%M%S"), len(_race_store) + 1),
            "remark": remark,
            "created": _now(),
        }
        _race_store.insert(0, rec)
    return ok(rec)


@bp.get("/race/list")
def race_list():
    with _lock:
        return ok({"records": list(_race_store)})
