# -*- coding: utf-8 -*-
"""加密数据场景接口：传输加密 / 展示脱敏 / 密文存储 / 报文整体加密签名。

统一响应：{ code, data, message }，code=0 成功，非 0 为业务失败（HTTP 仍为 200，便于前端读取 message）。
错误码约定：
    1001 明文传输被拒绝        1002 查看过于频繁        1003 密钥未命中/已轮换
    2001 报文时间戳过期        2002 报文签名校验失败    2003 解密失败
"""
import hashlib
import json
import random
import threading
import time

from flask import Blueprint, jsonify, request

import crypto_util as cu
import vault_db
from config import Config

bp = Blueprint("crypto_api", __name__)

_lock = threading.Lock()


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "data": data, "message": message})


def fail(message, code=1):
    return jsonify({"code": code, "data": None, "message": message})


def body():
    return request.get_json(silent=True) or {}


# ==================================================================
# 通用加解密通道（浏览器不支持 Web Crypto 时的降级入口 / 脚本侧"解密 SDK"雏形）
# ==================================================================
@bp.get("/crypto/pubkey")
def pubkey():
    """签发 RSA 公钥（带随机网络延迟，模拟密钥服务）。"""
    lo, hi = Config.CRYPTO_PUBKEY_DELAY_RANGE
    time.sleep(random.uniform(lo, hi))
    return ok({
        "alg": "RSA-OAEP-SHA1",
        "keyVersion": cu.RSA_KEY_VERSION,
        "publicKeyPem": cu.RSA_PUBLIC_PEM,
        "fingerprint": cu.RSA_FINGERPRINT,
        "issuedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
    })


@bp.post("/crypto/pubkey/rotate")
def pubkey_rotate():
    """重新签发密钥对：轮换前获取的报文将无法解开。"""
    fp = cu.rotate_rsa()
    return ok({"fingerprint": fp, "keyVersion": cu.RSA_KEY_VERSION, "rotated": True})


@bp.get("/crypto/session-key")
def session_key():
    """下发会话对称密钥（演示用；真实系统的会话密钥由登录票据派生，不会明文下发）。"""
    return ok({
        "alg": "AES-GCM-256",
        "keyB64": cu.aes_key_b64(),
        "keyVersion": cu.CURRENT_KEY_VERSION,
        "ivLen": 12,
    })


@bp.post("/crypto/encrypt")
def encrypt_text():
    payload = body()
    plain = payload.get("plain") or ""
    alg = payload.get("alg") or "AES-GCM"
    version = payload.get("keyVersion")
    if alg == "RSA-OAEP":
        return ok({"alg": alg, "cipherB64": cu.rsa_encrypt_b64(plain), "ivB64": None,
                   "keyVersion": cu.RSA_KEY_VERSION})
    box = cu.aes_encrypt(plain, version)
    return ok({"alg": "AES-GCM-256", **box})


@bp.post("/crypto/decrypt")
def decrypt_text():
    payload = body()
    alg = payload.get("alg") or "AES-GCM"
    cipher = payload.get("cipherB64") or ""
    try:
        if alg == "RSA-OAEP":
            text = cu.rsa_decrypt_b64(cipher)
        else:
            text = cu.aes_decrypt(cipher, payload.get("ivB64"), payload.get("keyVersion"))
    except ValueError as ex:
        return fail(str(ex), code=2003)
    return ok({"plainText": text})


# ==================================================================
# E-01 传输加密：表单值在 DOM 里是明文，请求体里是密文
# ==================================================================
@bp.post("/crypto/login/encrypted")
def login_encrypted():
    payload = body()
    account = (payload.get("account") or "").strip()
    credential = payload.get("credentialB64") or ""
    version = payload.get("keyVersion") or ""
    if not credential:
        return fail("缺少密文字段 credentialB64")

    try:
        revealed = cu.rsa_decrypt_b64(credential)
    except ValueError as ex:
        # 典型触发：点过「轮换密钥」后仍提交轮换前的旧密文
        return fail(str(ex), code=1003)

    # 服务端解密成功即可，但**绝不回显明文口令**（真实系统的红线）：
    # 只返回解密结果的 SHA-256 前 16 位与掩码，脚本需自己按同样算法算摘要后比对
    digest = hashlib.sha256(revealed.encode("utf-8")).hexdigest()[:16].upper()
    if len(revealed) <= 4:
        masked = "*" * len(revealed)
    else:
        masked = revealed[:2] + "*" * (len(revealed) - 4) + revealed[-2:]

    data = {
        "account": account,
        "credentialLen": len(credential),
        "keyVersion": version or cu.RSA_KEY_VERSION,
        "decrypted": True,
        "serverDigest": digest,
        "maskedPassword": masked,
        "serverTime": time.strftime("%H:%M:%S"),
    }
    # 练习后门：默认关闭；打开后才会额外回显服务端解出的明文口令
    if Config.CRYPTO_ECHO_PLAINTEXT:
        data["revealedPassword"] = revealed
    return ok(data)


@bp.post("/crypto/login/plain")
def login_plain():
    """对照组：服务端已强制 HTTPS + 字段加密，明文通道直接被拒绝。"""
    payload = body()
    return fail(
        "服务端拒绝：检测到明文密码传输（账号 %s），请使用公钥加密后提交"
        % (payload.get("account") or "-"),
        code=1001,
    )


# ==================================================================
# E-02 展示脱敏：页面只有掩码，完整值必须额外取数
# ==================================================================
# (id, cust_no, cust_name, mobile, idcard, balance, 是否在 DOM 上附带 data-raw 明文)
_MASKED_SOURCE = [
    (1, "C-2001", "启元资产管理有限公司", "13812348000", "310101199203078123", "862300.00", False),
    (2, "C-2002", "恒信证券自营账户", "13905718888", "310101198811224517", "512000.00", False),
    (3, "C-2003", "南方稳健混合型基金", "13600129876", "440301199507113326", "304800.00", True),
    (4, "C-2004", "天元量化三号私募", "15021097788", "120103198209054411", None, False),
    (5, "C-2005", "星海信托单一计划", "13712346688", "110105199309126657", "98650.00", False),
]

_reveal_log = {}  # id -> 上次放行时间戳（模拟审计 + 限流）


def _masked_row(t):
    rid, no, name, mobile, idcard, balance, has_raw = t
    return {
        "id": rid,
        "custNo": no,
        "custName": name,
        "mobileMasked": cu.mask_mobile(mobile),
        "idcardMasked": cu.mask_idcard(idcard),
        "balanceMasked": cu.mask_amount(balance),
        # 个别字段被前端顺手塞进了 data-raw 属性（真实项目的常见泄漏点）
        "hasRawAttr": has_raw,
        "rawHint": mobile if has_raw else None,
    }


@bp.get("/crypto/masked/customers")
def masked_customers():
    time.sleep(random.uniform(0.2, 0.5))
    return ok({"rows": [_masked_row(t) for t in _MASKED_SOURCE], "total": len(_MASKED_SOURCE)})


@bp.post("/crypto/masked/reveal")
def masked_reveal():
    payload = body()
    rid = int(payload.get("id") or 0)
    row = next((t for t in _MASKED_SOURCE if t[0] == rid), None)
    if not row:
        return fail("客户不存在：%s" % rid)

    cooldown = Config.CRYPTO_REVEAL_COOLDOWN
    last = _reveal_log.get(rid)
    if last and time.time() - last < cooldown:
        return fail("查看过于频繁，剩余冷却 %d 秒" % int(cooldown - (time.time() - last)), code=1002)

    _reveal_log[rid] = time.time()
    _, no, name, mobile, idcard, balance, _ = row
    return ok({
        "id": rid,
        "custNo": no,
        "custName": name,
        "plain": {"mobile": mobile, "idcard": idcard, "balance": balance},
        "cooldownSeconds": cooldown,
        "auditLog": "%s 查看了客户 %s 的敏感字段" % (time.strftime("%H:%M:%S"), no),
    })


@bp.get("/crypto/masked/raw")
def masked_raw():
    """服务端全量明文（稳定数据源）：断言敏感值时应以这里为准，而非页面文本。"""
    rows = [{
        "id": t[0], "custNo": t[1], "custName": t[2],
        "mobile": t[3], "idcard": t[4], "balance": t[5],
    } for t in _MASKED_SOURCE]
    return ok({"rows": rows, "total": len(rows)})


# ==================================================================
# E-03 密文存储核对：页面明文来自服务端解密，库中是 AES-GCM 密文
# ==================================================================
def _decrypt_row(r):
    mobile = cu.try_aes_decrypt(r["mobile_enc"], r["mobile_iv"], r["key_version"])
    idcard = cu.try_aes_decrypt(r["idcard_enc"], r["idcard_iv"], r["key_version"])
    balance = cu.try_aes_decrypt(r["balance_enc"], r["balance_iv"], r["key_version"])
    return {
        "id": r["id"],
        "custNo": r["cust_no"],
        "custName": r["cust_name"],
        "keyVersion": r["key_version"],
        "updatedAt": r["updated_at"],
        "note": r["note"],
        "mobile": mobile["text"],
        "mobileState": "fail" if not mobile["ok"] else ("null" if mobile["text"] is None else "ok"),
        "mobileReason": mobile.get("reason"),
        "idcard": idcard["text"],
        "idcardState": "fail" if not idcard["ok"] else ("null" if idcard["text"] is None else "ok"),
        "balance": balance["text"],
        "balanceState": "fail" if not balance["ok"] else ("null" if balance["text"] is None else "ok"),
    }


@bp.get("/crypto/vault/page")
def vault_page():
    page = max(1, int(request.args.get("page") or 1))
    size = int(request.args.get("size") or Config.CRYPTO_PAGE_SIZE)
    rows = [_decrypt_row(r) for r in vault_db.raw_rows()]
    total = len(rows)
    start = (page - 1) * size
    pages = (total + size - 1) // size
    time.sleep(Config.DB_WRITE_DELAY)
    return ok({"rows": rows[start:start + size], "total": total,
               "page": page, "size": size, "pages": pages})


@bp.get("/crypto/vault/db/query")
def vault_db_query():
    """库表原始行：只有密文、IV 与摘要，没有明文。"""
    return ok({
        "rows": vault_db.raw_rows(),
        "note": "敏感字段均为 AES-256-GCM 密文（base64），需按 key_version 取对应密钥解密后比对",
    })


@bp.get("/crypto/vault/db/meta")
def vault_db_meta():
    return ok(vault_db.meta())


@bp.post("/crypto/vault/decrypt")
def vault_decrypt():
    payload = body()
    cipher = payload.get("cipherB64") or ""
    version = payload.get("keyVersion") or cu.CURRENT_KEY_VERSION
    res = cu.try_aes_decrypt(cipher, payload.get("ivB64"), version)
    if res["text"] is None and res["ok"]:
        return fail("该字段未登记（NULL）", code=2003)
    if not res["ok"]:
        return fail(res["reason"], code=2003)
    return ok({"plainText": res["text"], "keyVersion": version})


@bp.post("/crypto/vault/write")
def vault_write():
    """登记新档案：明文入库前加密。相同明文重复写入会得到完全不同的密文。"""
    payload = body()
    mobile = (payload.get("mobile") or "").strip()
    if not mobile:
        return fail("手机号不能为空")
    no = (payload.get("custNo") or "").strip() or ("C-%d" % (2000 + int(time.time()) % 1000))
    name = (payload.get("custName") or "").strip() or "未命名客户"
    idcard = (payload.get("idcard") or "").strip() or None
    balance = (payload.get("balance") or "").strip() or None

    new_id = vault_db.insert_profile(no, name, mobile, idcard, balance)
    row = next((r for r in vault_db.raw_rows() if r["id"] == new_id), None)
    same_rows = [r for r in vault_db.raw_rows()
                 if r["mobile_hmac"] and row and r["mobile_hmac"] == row["mobile_hmac"]]
    return ok({
        "id": new_id,
        "row": _decrypt_row(row) if row else None,
        "cipherStored": {"mobileEnc": row["mobile_enc"][:48] + "..." if row else None,
                         "ivB64": row["mobile_iv"] if row else None,
                         "keyVersion": row["key_version"] if row else None},
        # 同明文密文条数（>1 说明密文必然不同，不能用密文做相等断言）
        "samePlainCount": len(same_rows),
    })


@bp.post("/crypto/vault/reset")
def vault_reset():
    vault_db.reset_vault()
    return ok({"rows": vault_db.count_rows(), "reset": True})


# ==================================================================
# E-04 报文整体加密 + 签名
# ==================================================================
_ENVELOPE_ROWS = [
    {"tradeNo": "T-20260917-0001", "customer": "启元资产管理有限公司", "amount": 1286500.00, "status": "已清算"},
    {"tradeNo": "T-20260917-0002", "customer": "恒信证券自营账户", "amount": 512000.00, "status": "已清算"},
    {"tradeNo": "T-20260917-0003", "customer": "南方稳健混合型基金", "amount": 304800.00, "status": "待清算"},
    {"tradeNo": "T-20260917-0004", "customer": "天元量化三号私募", "amount": 52862.50, "status": "已清算"},
    {"tradeNo": "T-20260917-0005", "customer": "星海信托单一计划", "amount": 98650.00, "status": "待清算"},
]


def _build_envelope(mode="normal"):
    ts = cu.now_ts()
    plain = json.dumps({"rows": _ENVELOPE_ROWS}, ensure_ascii=False)
    box = cu.aes_encrypt(plain)
    if mode == "expired":
        # 时间戳超出有效窗口：签名本身是对的，但报文已过期
        ts -= Config.CRYPTO_TS_WINDOW + 480
    sign = cu.sign_payload(ts, box["cipherB64"])
    if mode == "tampered":
        # 签名位翻转：模拟报文被中间人改写
        sign = ("0" if sign[0] != "0" else "1") + sign[1:]
    return {
        "alg": "AES-256-GCM",
        "keyVersion": box["keyVersion"],
        "encB64": box["cipherB64"],
        "ivB64": box["ivB64"],
        "ts": ts,
        "sign": sign,
        "mode": mode,
        "rowCount": len(_ENVELOPE_ROWS),
    }


@bp.get("/crypto/envelope")
def envelope():
    mode = request.args.get("mode") or "normal"
    time.sleep(random.uniform(0.3, 0.9))
    return ok(_build_envelope(mode))


@bp.post("/crypto/envelope/verify")
def envelope_verify():
    """客户端侧“验签 SDK”：先校时间戳窗口，再校 HMAC 签名。"""
    payload = body()
    try:
        ts = int(payload.get("ts"))
    except (TypeError, ValueError):
        return fail("报文缺少合法时间戳 ts", code=2001)

    enc = payload.get("encB64") or ""
    sign = payload.get("sign") or ""
    age = abs(cu.now_ts() - ts)
    if age > Config.CRYPTO_TS_WINDOW:
        return fail("报文时间戳已过期：偏差 %d 秒，超出 %d 秒有效窗口"
                    % (age, Config.CRYPTO_TS_WINDOW), code=2001)
    if not _cmp_sig(cu.sign_payload(ts, enc), sign):
        return fail("报文签名校验失败：内容已被篡改", code=2002)
    return ok({"valid": True, "ageSeconds": age, "checkedAt": time.strftime("%H:%M:%S")})


def _cmp_sig(a, b):
    if len(a) != len(b):
        return False
    diff = 0
    for x, y in zip(a, b):
        diff |= ord(x) ^ ord(y)
    return diff == 0
