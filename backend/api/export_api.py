# -*- coding: utf-8 -*-
"""异步导出长任务：后台线程推进进度，完成后可下载生成文件。"""
import csv
import io
import random
import threading
import time
import uuid

from flask import Blueprint, jsonify, send_file

from config import Config

bp = Blueprint("export_api", __name__)

_tasks = {}
_lock = threading.Lock()
_STATES = ("pending", "running", "done", "error")


def _worker(task_id):
    total = Config.EXPORT_STEPS
    with _lock:
        task = _tasks[task_id]
    try:
        for step in range(1, total + 1):
            time.sleep(Config.EXPORT_STEP_INTERVAL)
            with _lock:
                task["progress"] = round(step / total * 100)
            # 每个任务自带轻微随机扰动，避免极端规律化
            if random.random() < 0.02:
                time.sleep(0.3)
        with _lock:
            task["state"] = "done"
    except Exception as exc:  # noqa: BLE001
        with _lock:
            task["state"] = "error"
            task["error"] = str(exc)


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "data": data, "message": message})


def fail(message, code=1):
    return jsonify({"code": code, "data": None, "message": message})


@bp.post("/export/start")
def export_start():
    task_id = uuid.uuid4().hex[:12]
    with _lock:
        _tasks[task_id] = {
            "task_id": task_id,
            "state": "pending",
            "progress": 0,
            "created": time.strftime("%H:%M:%S"),
        }
    threading.Thread(target=_worker, args=(task_id,), daemon=True).start()
    return ok({"task_id": task_id})


@bp.get("/export/status/<task_id>")
def export_status(task_id):
    with _lock:
        task = _tasks.get(task_id)
    if not task:
        return fail("任务不存在或已过期", code=404), 404
    return ok(
        {
            "task_id": task["task_id"],
            "state": task["state"],
            "progress": task["progress"],
        }
    )


@bp.get("/export/file/<task_id>")
def export_file(task_id):
    with _lock:
        task = _tasks.get(task_id)
    if not task:
        return fail("任务不存在", code=404), 404
    if task["state"] != "done":
        return fail("任务尚未完成", code=400), 400

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["序号", "单号", "客户", "金额", "状态", "生成时间"])
    for i in range(1, Config.EXPORT_ROW_COUNT + 1):
        writer.writerow(
            [
                i,
                "BILL-%s-%05d" % (task_id.upper(), i),
                "客户%05d" % i,
                round(random.uniform(10, 5000), 2),
                random.choice(["已完成", "进行中", "已退款"]),
                time.strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )
    data = buf.getvalue().encode("utf-8-sig")
    return send_file(
        io.BytesIO(data),
        mimetype="text/csv",
        as_attachment=True,
        download_name="export_%s.csv" % task_id,
    )
