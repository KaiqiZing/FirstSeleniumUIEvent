# -*- coding: utf-8 -*-
"""图形验证码：Pillow 生成 PNG，答案按 sid 存内存；支持配置万能验证码。"""
import base64
import io
import random
import string
import time
import uuid

from flask import Blueprint, jsonify, request

from config import Config

bp = Blueprint("captcha_api", __name__)

_storage = {}


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "data": data, "message": message})


def fail(message, code=1):
    return jsonify({"code": code, "data": None, "message": message})


def _random_color(low, high):
    return (random.randint(low, high), random.randint(low, high), random.randint(low, high))


@bp.get("/captcha")
def captcha_image():
    from PIL import Image, ImageDraw, ImageFont

    width, height = 140, 48
    code = "".join(random.choices(Config.CAPTCHA_CHARS, k=4))

    image = Image.new("RGB", (width, height), _random_color(235, 250))
    draw = ImageDraw.Draw(image)

    font = None
    for candidate in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ):
        try:
            font = ImageFont.truetype(candidate, 30)
            break
        except Exception:  # noqa: BLE001
            continue
    if font is None:
        font = ImageFont.load_default()

    # 干扰线
    for _ in range(4):
        draw.line(
            [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height)),
            ],
            fill=_random_color(120, 200),
            width=1,
        )
    # 字符
    for idx, ch in enumerate(code):
        draw.text(
            (12 + idx * 30 + random.randint(-2, 2), random.randint(2, 10)),
            ch,
            font=font,
            fill=_random_color(30, 110),
        )
    # 噪点
    for _ in range(120):
        draw.point(
            (random.randint(0, width - 1), random.randint(0, height - 1)),
            fill=_random_color(0, 255),
        )

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    sid = uuid.uuid4().hex[:16]
    _storage[sid] = {"code": code, "expire": time.time() + Config.CAPTCHA_EXPIRE_SECONDS}

    data_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    return ok({"sid": sid, "image": data_url})


@bp.post("/captcha/verify")
def captcha_verify():
    payload = request.get_json(silent=True) or {}
    sid = (payload.get("sid") or "").strip()
    code = (payload.get("code") or "").strip().upper()

    if not sid or not code:
        return fail("请输入验证码")
    if code == Config.CAPTCHA_UNIVERSAL_CODE and Config.CAPTCHA_UNIVERSAL_ENABLED:
        return ok({"passed": True, "via": "universal"})

    item = _storage.get(sid)
    if not item or time.time() > item["expire"]:
        _storage.pop(sid, None)
        return fail("验证码已过期，请刷新")
    _storage.pop(sid, None)
    if item["code"] != code:
        return fail("验证码不正确")
    return ok({"passed": True, "via": "typed"})
