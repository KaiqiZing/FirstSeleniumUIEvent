<template>
  <div class="page">
    <div class="page-title">E-03 客户档案密文存储</div>
    <p class="page-desc">档案敏感字段加密入库，页面展示服务端解密结果，明细按分页查询。</p>

    <section class="panel">
      <h3>档案明细</h3>
      <p class="p-sub">第 {{ page }} / {{ pages }} 页，共 {{ total }} 条。</p>
      <el-table v-loading="loading" :data="rows" border :row-class-name="vaultRowClass" style="width: 100%">
        <el-table-column prop="custNo" label="客户号" width="110" />
        <el-table-column prop="custName" label="客户名称" min-width="180" />
        <el-table-column label="联系手机" width="150">
          <template #default="{ row }">
            <span :class="['cell-val', 'v-' + row.mobileState]">{{ cellText(row, 'mobile') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="证件号码" width="180">
          <template #default="{ row }">
            <span :class="['cell-val', 'v-' + row.idcardState]">{{ cellText(row, 'idcard') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="结算余额" width="130" align="right">
          <template #default="{ row }">
            <span :class="['cell-val', 'v-' + row.balanceState]">{{ cellText(row, 'balance') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="密钥版本" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.keyVersion === curVersion ? 'success' : 'warning'" effect="plain">
              {{ row.keyVersion }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="toolbar">
        <el-button id="btn-page-prev" :disabled="page <= 1 || loading" @click="loadPage(page - 1)">上一页</el-button>
        <el-button id="btn-page-next" :disabled="page >= pages || loading" @click="loadPage(page + 1)">下一页</el-button>
        <el-button id="btn-db-query" @click="loadRaw">查询库表原始行</el-button>
        <el-button id="btn-db-meta" @click="loadMeta">查看库表信息</el-button>
      </div>
      <p v-if="meta" class="tiny muted mono">
        {{ meta.dbPath }} · {{ meta.alg }} · 当前密钥 {{ meta.currentKeyVersion }} · 行数 {{ meta.rows }} · 最后更新 {{ meta.lastUpdatedAt }}
      </p>
    </section>

    <section v-if="rawRows.length" class="panel">
      <h3>库表原始行（密文）</h3>
      <p class="p-sub">敏感字段在库中的真实形态，无法直接阅读。</p>
      <el-table :data="rawRows" border size="small" :row-class-name="rawRowClass" style="width: 100%">
        <el-table-column prop="cust_no" label="客户号" width="100" />
        <el-table-column label="mobile_enc" min-width="220">
          <template #default="{ row }"><span class="cipher mono">{{ clip(row.mobile_enc) }}</span></template>
        </el-table-column>
        <el-table-column label="mobile_iv" width="150">
          <template #default="{ row }"><span class="mono muted">{{ clip(row.mobile_iv, 16) }}</span></template>
        </el-table-column>
        <el-table-column label="检索摘要" width="130">
          <template #default="{ row }"><span class="mono muted">{{ clip(row.mobile_hmac, 12) }}</span></template>
        </el-table-column>
        <el-table-column prop="key_version" label="版本" width="76" align="center" />
        <el-table-column prop="updated_at" label="更新时间" width="150" />
      </el-table>
    </section>

    <section class="panel">
      <h3>新档案登记</h3>
      <p class="p-sub">明文入库前加密，同一手机号重复登记可观察密文是否一致。</p>
      <div class="row-form">
        <div class="fld">
          <span class="f-label">客户号</span>
          <input id="write-custno" v-model="form.custNo" class="el-input__inner" placeholder="C-2006" style="width: 130px" />
        </div>
        <div class="fld">
          <span class="f-label">客户名称</span>
          <input id="write-name" v-model="form.custName" class="el-input__inner" placeholder="请输入客户名称" style="width: 200px" />
        </div>
        <div class="fld">
          <span class="f-label">联系手机</span>
          <input id="write-mobile" v-model="form.mobile" class="el-input__inner" placeholder="请输入手机号" style="width: 170px" />
        </div>
        <div class="fld">
          <span class="f-label">结算余额</span>
          <input id="write-balance" v-model="form.balance" class="el-input__inner" placeholder="留空即为未登记" style="width: 150px" />
        </div>
        <el-button id="btn-write" type="primary" :loading="writing" @click="writeRow">登记</el-button>
      </div>
    </section>

    <section class="panel">
      <h3>密文解密核验</h3>
      <p class="p-sub">粘贴库中密文，按密钥版本还原明文。</p>
      <div class="row-form">
        <div class="fld">
          <span class="f-label">密文（base64）</span>
          <input id="decrypt-input" v-model="cipher" class="el-input__inner mono" placeholder="可先从上方原始行取一段密文" style="width: 420px" />
        </div>
        <div class="fld">
          <span class="f-label">IV（base64）</span>
          <input id="decrypt-iv" v-model="iv" class="el-input__inner mono" placeholder="与密文配套的 IV" style="width: 240px" />
        </div>
        <div class="fld">
          <span class="f-label">密钥版本</span>
          <el-select id="decrypt-keyversion" v-model="keyVersion" clearable placeholder="留空=当前版本" style="width: 160px">
            <el-option label="K2（当前）" value="K2" />
            <el-option label="K1（历史）" value="K1" />
            <el-option label="K0（已吊销）" value="K0" />
          </el-select>
        </div>
        <el-button id="btn-decrypt" :loading="decrypting" @click="decryptOne">解密</el-button>
        <el-button id="btn-vault-reset" type="danger" plain @click="resetVault">重置密文库</el-button>
      </div>
      <pre id="decrypt-output" class="wire mono">{{ decryptOut }}</pre>
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
import { ref, onMounted } from 'vue'
import http from '../../utils/http'

const rows = ref([])
const rawRows = ref([])
const meta = ref(null)
const page = ref(1)
const pages = ref(1)
const total = ref(0)
const curVersion = ref('')
const loading = ref(false)
const writing = ref(false)
const decrypting = ref(false)
const cipher = ref('')
const iv = ref('')
const keyVersion = ref('')
const decryptOut = ref('尚未解密')
const logs = ref([])
const form = ref({ custNo: '', custName: '', mobile: '', balance: '' })

const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })
const log = (text, err = false) => logs.value.unshift({ time: stamp(), text, err })

const vaultRowClass = ({ row }) => 'vault-row vault-row-' + row.id
const rawRowClass = ({ row }) => 'raw-row raw-row-' + row.id
const clip = (v, n = 32) => (v ? v.slice(0, n) + (v.length > n ? '…' : '') : '—')

function cellText(row, field) {
  const state = row[field + 'State']
  if (state === 'fail') return '解密失败'
  if (state === 'null') return '—'
  return row[field]
}

async function loadPage(p = 1) {
  loading.value = true
  try {
    const data = await http.get('/crypto/vault/page', { params: { page: p } })
    rows.value = data.rows
    page.value = data.page
    pages.value = data.pages
    total.value = data.total
    log(`已加载第 ${data.page} 页：${data.rows.length} 条（共 ${data.total} 条）`)
  } catch (err) {
    log(`档案加载失败：${err.message}`, true)
  } finally {
    loading.value = false
  }
}

async function loadRaw() {
  try {
    rawRows.value = (await http.get('/crypto/vault/db/query')).rows
    log(`已读取库表原始行：${rawRows.value.length} 行`)
  } catch (err) {
    log(`原始行读取失败：${err.message}`, true)
  }
}

async function loadMeta() {
  try {
    meta.value = await http.get('/crypto/vault/db/meta')
    curVersion.value = meta.value.currentKeyVersion
    log(`当前密钥版本 ${meta.value.currentKeyVersion}，库中行 ${meta.value.rows}`)
  } catch (err) {
    log(`库表信息读取失败：${err.message}`, true)
  }
}

async function writeRow() {
  writing.value = true
  try {
    const data = await http.post('/crypto/vault/write', { ...form.value })
    log(`登记成功：${data.row.custNo}，库记录 ${data.id}，同明文密文共 ${data.samePlainCount} 份（IV 随机 → 密文必不相同）`)
    log(`本次密文：${data.cipherStored.mobileEnc}`)
    await loadPage(page.value)
    await loadRaw()
  } catch (err) {
    log(`登记失败：${err.message}`, true)
  } finally {
    writing.value = false
  }
}

async function decryptOne() {
  decrypting.value = true
  try {
    const payload = { cipherB64: cipher.value, ivB64: iv.value }
    if (keyVersion.value) payload.keyVersion = keyVersion.value
    const data = await http.post('/crypto/vault/decrypt', payload)
    decryptOut.value = data.plainText
    log(`解密成功（${data.keyVersion}）：${data.plainText}`)
  } catch (err) {
    decryptOut.value = '解密失败：' + err.message
    log(`解密失败：${err.message}`, true)
  } finally {
    decrypting.value = false
  }
}

async function resetVault() {
  try {
    const data = await http.post('/crypto/vault/reset', {})
    log(`密文库已重置：${data.rows} 行`)
    await loadPage(1)
    await loadRaw()
    await loadMeta()
  } catch (err) {
    log(`重置失败：${err.message}`, true)
  }
}

onMounted(async () => {
  await loadPage(1)
  await loadMeta()
})
</script>

<style scoped>
.cell-val.fail { color: var(--danger); }
.cell-val.null { color: var(--text-3); }
.cipher { color: #7c6bb0; font-size: 12px; }
.wire {
  margin: 12px 0 0;
  background: #1a1a1a;
  color: #bfe6cf;
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-all;
  min-height: 46px;
}
.tiny { font-size: 12px; margin: 10px 0 0; }
</style>
