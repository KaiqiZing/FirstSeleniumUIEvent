<template>
  <div class="page">
    <div class="page-title">E-04 接口报文加密传输</div>
    <p class="page-desc">成交明细接口返回加密报文，客户端本地解密后渲染，并校验时间戳与签名。</p>

    <section class="panel">
      <h3>报文拉取</h3>
      <p class="p-sub">选择通道状态后拉取当日成交明细。</p>
      <div class="row-form">
        <el-radio-group id="mode-group" v-model="mode">
          <el-radio value="normal">正常报文</el-radio>
          <el-radio value="expired">过期时间戳</el-radio>
          <el-radio value="tampered">签名被篡改</el-radio>
        </el-radio-group>
        <el-button id="btn-fetch-envelope" type="primary" :loading="fetching" @click="fetchEnvelope">
          拉取加密报文
        </el-button>
        <el-button id="btn-verify-envelope" :disabled="!env" :loading="verifying" @click="verifyEnvelope">
          校验此报文
        </el-button>
      </div>
    </section>

    <section v-if="env" class="panel">
      <h3>服务端原始报文</h3>
      <p class="p-sub">通道上传输的内容，不含任何明文。</p>
      <div class="kv">
        <div class="kv-item"><span class="k">算法</span><span class="v mono">{{ env.alg }} / {{ env.keyVersion }}</span></div>
        <div class="kv-item"><span class="k">时间戳</span><span id="envelope-ts" class="v mono strong">{{ env.ts }}</span></div>
        <div class="kv-item"><span class="k">记录数</span><span class="v mono">{{ env.rowCount }}</span></div>
        <div class="kv-item"><span class="k">IV</span><span class="v mono">{{ env.ivB64 }}</span></div>
      </div>
      <div class="kv-item col">
        <span class="k">签名</span><span id="envelope-sign" class="v mono">{{ env.sign }}</span>
      </div>
      <div class="kv-item col">
        <span class="k">密文</span><span id="envelope-enc" class="v mono cipher">{{ env.encB64 }}</span>
      </div>
    </section>

    <section v-if="decoded.length" class="panel">
      <h3>解密后的成交明细</h3>
      <p class="p-sub">共 {{ decoded.length }} 条。</p>
      <el-table :data="decoded" border :row-class-name="envRowClass" style="width: 100%">
        <el-table-column prop="tradeNo" label="成交编号" width="180" />
        <el-table-column prop="customer" label="成交客户" min-width="200" />
        <el-table-column label="成交金额" width="150" align="right">
          <template #default="{ row }"><span class="env-amount mono">{{ money(row.amount) }}</span></template>
        </el-table-column>
        <el-table-column prop="status" label="清算状态" width="110" align="center" />
      </el-table>
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
import { ref } from 'vue'
import http from '../../utils/http'
import { aesDecrypt, webCryptoAvailable } from '../../utils/crypto'

const mode = ref('normal')
const env = ref(null)
const decoded = ref([])
const fetching = ref(false)
const verifying = ref(false)
const logs = ref([])
let sessionKey = null

const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })
const log = (text, err = false) => logs.value.unshift({ time: stamp(), text, err })
const money = (v) => '¥' + Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const envRowClass = ({ row }) => 'env-row t-' + row.tradeNo

async function ensureSessionKey() {
  if (!sessionKey) sessionKey = await http.get('/crypto/session-key')
  return sessionKey
}

async function fetchEnvelope() {
  fetching.value = true
  try {
    env.value = await http.get('/crypto/envelope', { params: { mode: mode.value } })
    log(`已拉取 ${mode.value} 报文：密文长度 ${env.value.encB64.length}，时间戳 ${env.value.ts}`)
    await ensureSessionKey()
    let text
    if (webCryptoAvailable()) {
      text = await aesDecrypt(sessionKey.keyB64, env.value.ivB64, env.value.encB64)
    } else {
      text = (await http.post('/crypto/decrypt', {
        cipherB64: env.value.encB64,
        ivB64: env.value.ivB64,
        keyVersion: env.value.keyVersion
      })).plainText
    }
    decoded.value = JSON.parse(text).rows
    log(`本地解密成功：${decoded.value.length} 条成交明细`)
  } catch (err) {
    log(`报文处理失败：${err.message}`, true)
  } finally {
    fetching.value = false
  }
}

async function verifyEnvelope() {
  verifying.value = true
  try {
    const data = await http.post('/crypto/envelope/verify', {
      ts: env.value.ts,
      sign: env.value.sign,
      encB64: env.value.encB64
    })
    log(`签名校验通过：报文偏差 ${data.ageSeconds} 秒（${data.checkedAt}）`)
  } catch (err) {
    log(`签名校验未通过：${err.message}`, true)
  } finally {
    verifying.value = false
  }
}
</script>

<style scoped>
.kv { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 24px; }
.kv-item { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.kv-item.col { margin-top: 10px; align-items: flex-start; }
.kv-item .k { color: var(--text-3); width: 52px; flex: 0 0 auto; }
.kv-item .v { color: var(--text-1); word-break: break-all; }
.kv-item .v.strong { font-weight: 600; }
.cipher { color: #7c6bb0; font-size: 12px; }
</style>
