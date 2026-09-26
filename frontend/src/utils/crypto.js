// 浏览器侧加解密：优先使用 Web Crypto（crypto.subtle），非安全上下文降级，
// 降级时由服务端代加解密（等价于"注入式加解密 SDK"，便于脚本在任何环境下都能跑通）。
//
// 与后端 crypto_util.py 的对齐约定：
//   RSA-OAEP(SHA-1)  /  AES-256-GCM(iv 12 字节，密文尾部自带 16 字节 tag)

export const webCryptoAvailable = () => !!(window.crypto && window.crypto.subtle && window.isSecureContext)

export function b64ToBytes(b64) {
  const bin = atob(b64)
  const out = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i)
  return out
}

export function bytesToB64(bytes) {
  let bin = ''
  const arr = new Uint8Array(bytes)
  for (let i = 0; i < arr.length; i++) bin += String.fromCharCode(arr[i])
  return btoa(bin)
}

function pemToBytes(pem) {
  const body = pem.replace(/-----[A-Z ]+-----/g, '').replace(/\s+/g, '')
  return b64ToBytes(body)
}

export async function importRsaPublicKey(pem) {
  return crypto.subtle.importKey(
    'spki',
    pemToBytes(pem),
    { name: 'RSA-OAEP', hash: 'SHA-1' },
    true,
    ['encrypt']
  )
}

export async function importAesKey(keyB64, usages = ['encrypt', 'decrypt']) {
  return crypto.subtle.importKey('raw', b64ToBytes(keyB64), { name: 'AES-GCM' }, true, usages)
}

/** RSA-OAEP 加密 → base64 密文 */
export async function rsaEncrypt(pem, text) {
  const key = await importRsaPublicKey(pem)
  const ct = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, key, new TextEncoder().encode(text))
  return bytesToB64(ct)
}

/** AES-256-GCM 加密 → { cipherB64, ivB64 } */
export async function aesEncrypt(keyB64, text) {
  const key = await importAesKey(keyB64)
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, new TextEncoder().encode(text))
  return { cipherB64: bytesToB64(ct), ivB64: bytesToB64(iv) }
}

/** AES-256-GCM 解密 → 明文字符串 */
export async function aesDecrypt(keyB64, ivB64, cipherB64) {
  const key = await importAesKey(keyB64, ['decrypt'])
  const plain = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: b64ToBytes(ivB64) },
    key,
    b64ToBytes(cipherB64)
  )
  return new TextDecoder().decode(plain)
}

/**
 * 短指纹：文本取 sha256 前 8 字节（16 位十六进制大写）。
 * 口径与后端一致（crypto_api.login_encrypted 的 serverDigest = sha256(...)[:16].upper()），
 * E-01 用它本地算摘要与服务端回的摘要比对，从而在不回显明文的前提下验证"服务端解对了"。
 */
export async function shortDigest(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))
  return Array.from(new Uint8Array(buf).slice(0, 8))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
    .toUpperCase()
}
