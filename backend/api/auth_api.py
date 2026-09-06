# -*- coding: utf-8 -*-
"""会话登录：基于 Flask session（浏览器 Cookie）演示登录态与"记住我"。"""
from flask import Blueprint, jsonify, request, session

bp = Blueprint("auth_api", __name__)

_ACCOUNTS = {
    "tester": {"name": "测试员", "role": "自动化工程师"},
    "demo": {"name": "演示账号", "role": "访客"},
}


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "data": data, "message": message})


def fail(message, code=1, http=200):
    return jsonify({"code": code, "data": None, "message": message}), http


@bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    account = (payload.get("account") or "").strip()
    password = payload.get("password") or ""
    remember = bool(payload.get("remember"))

    if not account:
        return fail("请输入账号")
    if account not in _ACCOUNTS:
        return fail("账号不存在或密码错误")

    session["user"] = _ACCOUNTS[account]
    session["account"] = account
    session.permanent = remember
    return ok({"user": {**session["user"], "account": account}, "remember": remember})


@bp.get("/auth/me")
def me():
    user = session.get("user")
    if not user:
        return ok(None)
    return ok({**user, "account": session.get("account")})


@bp.post("/auth/logout")
def logout():
    session.clear()
    return ok({"loggedOut": True})
