# -*- coding: utf-8 -*-
"""加解密工具层：RSA-OAEP 传输加密 / AES-256-GCM 字段与报文加密 / HMAC-SHA256 报文签名。

跨语言对齐约定（前端 crypto.subtle 必须能解开后端产出，反之亦然）：
1. RSA-OAEP 统一使用 MGF1-SHA1 + OAEP-SHA1 —— 这是 Web Crypto `RSA-OAEP` 的默认且唯一内置组合。
2. AES 统一 256-GCM，nonce(iv) 固定 12 字节；密文与 tag 的排列为 `ciphertext || tag`，
   Python 的 AESGCM 与浏览器 Web Crypto 的 AES-GCM 语义完全一致，可直接互解。
3. 密钥版本：K2 为当前密钥，K1 为历史密钥（模拟密钥轮换后遗留的旧密文）。

注意：本文件用于演示「页面 dumb terminal、数据已加密」的自动化场景，密钥在进程启动时随机生成，
重启 Flask 即全部失效（旧密文无法解开），符合「清库重练」的设计。
"""
import base64
import hashlib
import hmac
import secrets
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---- 密钥版本 ----
CURRENT_KEY_VERSION = "K2"
LEGACY_KEY_VERSION = "K1"

# ---- 非对称密钥：每次进程启动随机生成一把新的 RSA-2048 ----
RSA_KEY_VERSION = "R1"
_RSA_KEY = None
_RSA_PUB_DER = b""
RSA_PUBLIC_PEM = ""
RSA_FINGERPRINT = ""


def _gen_rsa():
    global _RSA_KEY, _RSA_PUB_DER, RSA_PUBLIC_PEM, RSA_FINGERPRINT
    _RSA_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    _RSA_PUB_DER = _RSA_KEY.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    RSA_PUBLIC_PEM = _RSA_KEY.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")
    # 公钥指纹（便于人工/脚本确认本次会话使用的是哪把公钥）
    RSA_FINGERPRINT = hashlib.sha256(_RSA_PUB_DER).hexdigest()[:16].upper()


_gen_rsa()


def rotate_rsa():
    """重新签发 RSA 密钥对：轮换后用旧公钥加密的报文将无法解开（用于演示密钥轮换影响）。"""
    _gen_rsa()
    return RSA_FINGERPRINT

# ---- 对称密钥：当前版本与历史版本 ----
_AES_KEYS = {
    CURRENT_KEY_VERSION: secrets.token_bytes(32),
    LEGACY_KEY_VERSION: secrets.token_bytes(32),
}


def b64e(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))


# ------------------------------ RSA-OAEP ------------------------------
def rsa_encrypt_b64(plain: str) -> str:
    """服务端代加密（浏览器不支持 Web Crypto 时的降级通道，等价于前端 RSA 加密结果）。"""
    ct = _RSA_KEY.public_key().encrypt(
        plain.encode("utf-8"),
        padding.OAEP(mgf=padding.MGF1(hashes.SHA1()), algorithm=hashes.SHA1(), label=None),
    )
    return b64e(ct)


def rsa_decrypt_b64(cipher_b64: str) -> str:
    try:
        plain = _RSA_KEY.decrypt(
            b64d(cipher_b64),
            padding.OAEP(mgf=padding.MGF1(hashes.SHA1()), algorithm=hashes.SHA1(), label=None),
        )
    except Exception:
        # 密文不是本把公钥产出（换了一次会话的公钥 / 乱填），统一上抛给接口层
        raise ValueError("RSA 解密失败：密文与当前会话公钥不匹配")
    return plain.decode("utf-8")


# ------------------------------ AES-256-GCM ------------------------------
def aes_key_b64(version: str = None) -> str:
    return b64e(_AES_KEYS[version or CURRENT_KEY_VERSION])


def aes_encrypt(plain: str, version: str = None) -> dict:
    version = version or CURRENT_KEY_VERSION
    iv = secrets.token_bytes(12)
    ct = AESGCM(_AES_KEYS[version]).encrypt(iv, plain.encode("utf-8"), None)
    return {"cipherB64": b64e(ct), "ivB64": b64e(iv), "keyVersion": version}


def aes_decrypt(cipher_b64: str, iv_b64: str, version: str = None) -> str:
    version = version or CURRENT_KEY_VERSION
    if version not in _AES_KEYS:
        raise ValueError("未知的密钥版本：%s" % version)
    if version != CURRENT_KEY_VERSION:
        # 历史版本密钥仍在密钥库中，正常解开；若密文与版本不符走下面的 InvalidTag 分支
        pass
    try:
        plain = AESGCM(_AES_KEYS[version]).decrypt(b64d(iv_b64), b64d(cipher_b64), None)
    except Exception:
        raise ValueError("AES 解密失败：密文已被篡改或不属于密钥版本 %s" % version)
    return plain.decode("utf-8")


def legacy_encrypt(plain: str) -> dict:
    """用历史密钥加密（模拟密钥轮换前落库的旧密文）。"""
    return aes_encrypt(plain, LEGACY_KEY_VERSION)


def try_aes_decrypt(cipher_b64, iv_b64, version) -> dict:
    """不抛错的解密包装：返回 {ok, text, reason}，便于批量行处理。"""
    if cipher_b64 is None:
        return {"ok": True, "text": None, "reason": "字段未登记（NULL）"}
    try:
        return {"ok": True, "text": aes_decrypt(cipher_b64, iv_b64, version)}
    except ValueError as ex:
        return {"ok": False, "text": None, "reason": str(ex)}


# ------------------------------ HMAC-SHA256 报文签名 ------------------------------
SIGN_SECRET = secrets.token_bytes(32)


def sign_payload(ts: int, enc_b64: str) -> str:
    body = ("%d|%s" % (ts, enc_b64)).encode("utf-8")
    return hmac.new(SIGN_SECRET, body, hashlib.sha256).hexdigest()


def now_ts() -> int:
    return int(time.time())


# ------------------------------ 摘要（用于密文等值检索） ------------------------------
def indexed_hmac(value: str) -> str:
    """密文字段的确定性检索摘要：相同明文得到相同摘要，可直接用于等值查询。"""
    return hmac.new(SIGN_SECRET, value.encode("utf-8"), hashlib.sha256).hexdigest()[:32]


def mask_mobile(mobile: str) -> str:
    return mobile[:3] + "****" + mobile[-4:] if len(mobile) >= 7 else "****"


def mask_idcard(idcard: str) -> str:
    if len(idcard) < 8:
        return "****"
    return idcard[:4] + "*" * (len(idcard) - 8) + idcard[-4:]


def mask_amount(amount_str: str) -> str:
    return "¥ ****.**" if amount_str else "—"
