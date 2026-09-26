<template>
  <div class="page">
    <div class="page-title">E-01 传输加密登录</div>
    <p class="page-desc">结算系统登录，敏感字段经公钥加密后提交，服务端解密校验。</p>

    <section class="panel">
      <h3>通道密钥</h3>
      <p class="p-sub">每次会话由密钥服务签发一把公钥，敏感字段在本地完成加密。</p>
      <div class="kv">
        <div class="kv-item">
          <span class="k">算法</span>
          <span class="v mono">{{ pub ? pub.alg : '签发中…' }}</span>
        </div>
        <div class="kv-item">
          <span class="k">密钥版本</span>
          <span class="v mono">{{ pub ? pub.keyVersion : '—' }}</span>
        </div>
        <div class="kv-item">
          <span class="k">公钥指纹</span>
          <span id="pubkey-fingerprint" class="v mono strong">{{ pub ? pub.fingerprint : '—' }}</span>
        </div>
        <div class="kv-item">
          <span class="k">签发时间</span>
          <span class="v mono">{{ pub ? pub.issuedAt : '—' }}</span>
        </div>
      </div>
      <div class="toolbar">
        <el-button id="btn-reload-pubkey" :loading="loading" @click="loadPubkey">重新签发公钥</el-button>
        <el-tag v-if="!pub" type="warning" effect="plain" class="state-tag">密钥未就绪</el-tag>
        <el-tag v-else type="success" effect="plain" class="state-tag">密钥已就绪</el-tag>
      </div>
    </section>

    <section class="panel">
      <h3>账户登录</h3>
      <p class="p-sub">登录后将进入清算工作台。</p>
      <div class="row-form">
        <div class="fld">
          <span class="f-label">账号</span>
          <input id="login-account" v-model="account" class="el-input__inner" placeholder="请输入资金账号" style="width: 220px" />
        </div>
        <div class="fld">
          <span class="f-label">登录密码</span>
          <input id="login-password" v-model="password" type="password" class="el-input__inner" placeholder="请输入登录密码" style="width: 220px" />
        </div>
        <el-button id="btn-submit-encrypted" type="primary" :loading="busy" @click="submitEncrypted">加密并提交</el-button>
        <el-button id="btn-submit-plain" @click="submitPlain">明文提交（旧通道）</el-button>
      </div>
      <p class="tiny muted">加密方式：{{ cryptoMode }}</p>
    </section>

    <section class="panel">
      <h3>最近一次请求报文</h3>
      <p class="p-sub">提交至服务端的实际内容。</p>
      <pre id="request-body" class="wire mono">{{ reqBody }}</pre>
      <div class="kv">
        <div class="kv-item">
          <span class="k">服务端摘要</span>
          <span id="server-digest" class="v mono strong">{{ result ? result.serverDigest : '—' }}</span>
        </div>
        <div class="kv-item">
          <span class="k">本地摘要</span>
          <span id="local-digest" class="v mono">{{ result && result.localDigest ? result.localDigest : '—' }}</span>
        </div>
        <div class="kv-item">
          <span class="k">掩码</span>
          <span id="masked-password" class="v mono">{{ result ? result.maskedPassword : '—' }}</span>
        </div>
        <div class="kv-item">
          <span class="k">摘要比对</span>
          <span id="digest-match" class="v mono">{{ matchText }}</span>
        </div>
      </div>
      <p class="tiny muted">服务端只回「解密结果的摘要」与掩码，不回显明文口令；脚本应自行按 SHA-256 前 16 位比对两者。</p>
    </section>

    <div class="result-box">
      <div class="label">操作结果</div>
      <div v-if="!logs.length" class="empty-hint">暂无操作记录</div>
      <div v-else class="logs">
        <div v-for="(l, i) in logs" :key="i" class="log-line">
          <span class="time">{{ l.time }}</span><span :class="{ err: l.err }">{{ l.text }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../utils/http'
import { rsaEncrypt, shortDigest, webCryptoAvailable } from '../../utils/crypto'

const pub = ref(null)
const loading = ref(false)
const busy = ref(false)
const account = ref('fund001')
const password = ref('')
const reqBody = ref('尚未发起请求')
const result = ref(null)
const logs = ref([])
const cryptoMode = webCryptoAvailable() ? '浏览器 Web Crypto（RSA-OAEP）' : '服务端代加密（当前非安全上下文）'

const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })
const log = (text, err = false) => logs.value.unshift({ time: stamp(), text, err })
const matchText = computed(() => {
  if (!result.value) return '—'
  if (!result.value.localDigest) return '未比对'
  return result.value.match ? '一致' : '不一致'
})

async function loadPubkey() {
  loading.value = true
  try {
    pub.value = await http.get('/crypto/pubkey')
    log(`通道公钥就绪：指纹 ${pub.value.fingerprint}（${pub.value.keyVersion}）`)
  } catch (err) {
    log(`公钥签发失败：${err.message}`, true)
  } finally {
    loading.value = false
  }
}

async function submitEncrypted() {
  if (!account.value || !password.value) {
    ElMessage.warning('请输入账号与密码')
    return
  }
  if (!pub.value) {
    log('当前尚未拿到公钥，无法加密提交', true)
    return
  }
  busy.value = true
  try {
    let credentialB64
    if (webCryptoAvailable()) {
      credentialB64 = await rsaEncrypt(pub.value.publicKeyPem, password.value)
    } else {
      const box = await http.post('/crypto/encrypt', { alg: 'RSA-OAEP', plain: password.value })
      credentialB64 = box.cipherB64
    }
    const payload = { account: account.value, credentialB64, keyVersion: pub.value.keyVersion }
    reqBody.value = JSON.stringify(payload, null, 2)
    const data = await http.post('/crypto/login/encrypted', payload)
    // 服务端只回摘要与掩码：本地按同样算法（SHA-256 前 16 位）算一遍后比对
    const localDigest = webCryptoAvailable() ? await shortDigest(password.value) : ''
    const match = localDigest ? data.serverDigest === localDigest : null
    result.value = {
      serverDigest: data.serverDigest,
      localDigest: localDigest || null,
      maskedPassword: data.maskedPassword,
      match
    }
    const tail = localDigest
      ? `本地 ${localDigest} → ${match ? '一致' : '不一致'}`
      : '当前环境无 Web Crypto，未做本地比对'
    log(`加密提交成功：密文长度 ${data.credentialLen}，服务端解密成功，摘要 ${data.serverDigest}（${tail}，${data.serverTime}）`)
  } catch (err) {
    log(`加密提交失败：${err.message}`, true)
  } finally {
    busy.value = false
  }
}

async function submitPlain() {
  if (!account.value || !password.value) {
    ElMessage.warning('请输入账号与密码')
    return
  }
  const payload = { account: account.value, password: password.value }
  reqBody.value = JSON.stringify(payload, null, 2)
  result.value = null
  try {
    await http.post('/crypto/login/plain', payload)
    log('明文提交成功')
  } catch (err) {
    log(`明文提交失败：${err.message}`, true)
  }
}

onMounted(loadPubkey)
</script>

<style scoped>
.kv { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 24px; }
.kv-item { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.kv-item .k { color: var(--text-3); width: 68px; flex: 0 0 auto; }
.kv-item .v { color: var(--text-1); word-break: break-all; }
.kv-item .v.strong { font-weight: 600; }
.state-tag { margin-left: 4px; }
.wire {
  margin: 0;
  background: #1a1a1a;
  color: #bfe6cf;
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-all;
  min-height: 90px;
}
.tiny { font-size: 12px; margin: 10px 0 0; }
</style>
