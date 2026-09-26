<template>
  <div class="page">
    <div class="page-title">E-02 敏感字段脱敏展示</div>
    <p class="page-desc">客户档案列表按最小可见原则脱敏展示，完整信息需逐条申请查看。</p>

    <section class="panel">
      <h3>客户档案</h3>
      <p class="p-sub">共 {{ total }} 条，敏感字段默认以掩码呈现。</p>
      <el-table v-loading="loading" :data="rows" border :row-class-name="rowClass" style="width: 100%">
        <el-table-column prop="custNo" label="客户号" width="110" />
        <el-table-column prop="custName" label="客户名称" min-width="170" />
        <el-table-column label="联系手机" width="150">
          <template #default="{ row }">
            <span class="cell-mobile mono" :data-raw="row.rawHint">{{ row.mobileMasked }}</span>
          </template>
        </el-table-column>
        <el-table-column label="证件号码" width="190">
          <template #default="{ row }">
            <span class="cell-idcard mono">{{ row.idcardMasked }}</span>
          </template>
        </el-table-column>
        <el-table-column label="结算余额" width="130" align="right">
          <template #default="{ row }">
            <span class="cell-balance mono">{{ row.balanceMasked }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button :id="'btn-reveal-' + row.id" size="small" type="primary" plain @click="reveal(row)">
              申请查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="toolbar">
        <el-button id="btn-load-customers" @click="loadRows">刷新档案列表</el-button>
        <el-button id="btn-server-raw" @click="loadRaw">导出服务端原始数据</el-button>
      </div>
    </section>

    <el-drawer v-model="drawer" title="敏感信息查看" size="420px">
      <template v-if="cur">
        <div class="drawer-tip">
          <span id="reveal-countdown">{{ countdown }}</span> 秒后自动收起
        </div>
        <div class="drawer-row"><span>客户号</span><b class="mono">{{ cur.custNo }}</b></div>
        <div class="drawer-row"><span>联系手机</span><b id="reveal-mobile" class="mono">{{ plain.mobile }}</b></div>
        <div class="drawer-row"><span>证件号码</span><b id="reveal-idcard" class="mono">{{ plain.idcard }}</b></div>
        <div class="drawer-row"><span>结算余额</span><b id="reveal-balance" class="mono">{{ plain.balance || '—' }}</b></div>
      </template>
    </el-drawer>

    <section v-if="rawRows.length" class="panel">
      <h3>服务端原始数据</h3>
      <p class="p-sub">取自服务端解密接口，未做掩码处理。</p>
      <el-table :data="rawRows" border size="small" :row-class-name="rawRowClass" style="width: 100%">
        <el-table-column prop="custNo" label="客户号" width="110" />
        <el-table-column label="联系手机" width="150">
          <template #default="{ row }"><span class="raw-mobile mono">{{ row.mobile }}</span></template>
        </el-table-column>
        <el-table-column label="证件号码" width="190">
          <template #default="{ row }"><span class="raw-idcard mono">{{ row.idcard }}</span></template>
        </el-table-column>
        <el-table-column label="结算余额" width="130" align="right">
          <template #default="{ row }"><span class="raw-balance mono">{{ row.balance || '—' }}</span></template>
        </el-table-column>
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import http from '../../utils/http'

const rows = ref([])
const rawRows = ref([])
const total = ref(0)
const loading = ref(false)
const drawer = ref(false)
const cur = ref(null)
const plain = ref({})
const countdown = ref(0)
const logs = ref([])

let timer = null

const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })
const log = (text, err = false) => logs.value.unshift({ time: stamp(), text, err })

const rowClass = ({ row }) => 'cust-row row-' + row.id
const rawRowClass = ({ row }) => 'raw-row raw-row-' + row.id

async function loadRows() {
  loading.value = true
  try {
    const data = await http.get('/crypto/masked/customers')
    rows.value = data.rows
    total.value = data.total
    log(`档案列表已刷新：${data.total} 条`)
  } catch (err) {
    log(`档案列表加载失败：${err.message}`, true)
  } finally {
    loading.value = false
  }
}

async function loadRaw() {
  try {
    const data = await http.get('/crypto/masked/raw')
    rawRows.value = data.rows
    log(`已取服务端原始数据：${data.total} 条`)
  } catch (err) {
    log(`原始数据加载失败：${err.message}`, true)
  }
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

async function reveal(row) {
  try {
    const data = await http.post('/crypto/masked/reveal', { id: row.id })
    cur.value = data
    plain.value = data.plain
    countdown.value = data.cooldownSeconds
    drawer.value = true
    stopTimer()
    timer = setInterval(() => {
      countdown.value -= 1
      if (countdown.value <= 0) {
        stopTimer()
        drawer.value = false
        log(`客户 ${data.custNo} 的敏感信息已自动收起`)
      }
    }, 1000)
    log(`${data.auditLog}（${data.cooldownSeconds} 秒后自动收起）`)
  } catch (err) {
    log(`查看客户 ${row.custNo} 失败：${err.message}`, true)
  }
}

onMounted(loadRows)
onBeforeUnmount(stopTimer)
</script>

<style scoped>
.drawer-tip {
  font-size: 12px;
  color: var(--text-3);
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 16px;
}
.drawer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 4px;
  border-bottom: 1px dashed var(--border);
  font-size: 13px;
}
.drawer-row span { color: var(--text-3); }
</style>
