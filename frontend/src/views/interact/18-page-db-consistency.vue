<template>
  <div class="page">
    <div class="page-title">结算数据一致性核对</div>
    <p class="page-desc">
      分页展示结算明细与资金账户汇总；可通过「数据库查询」查看落库原始记录，金额在库中以「分」为单位存储。
    </p>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>结算明细</h3>
          <p class="p-sub">
            共 <b>{{ total }}</b> 条 / 第 {{ page }}/{{ pageCount }} 页
            <span class="snap">数据快照 {{ summary.snapshotAt }}</span>
          </p>
        </div>
        <div class="bar-actions">
          <el-button size="small" @click="refresh">刷新数据</el-button>
          <el-button size="small" @click="openDb">数据库查询</el-button>
          <el-button size="small" @click="postAccount">模拟清算入账</el-button>
          <el-button size="small" @click="reset">重置数据</el-button>
        </div>
      </div>

      <el-table :data="rows" size="small" border style="width: 100%" v-loading="loading">
        <el-table-column prop="itemNo" label="明细编号" width="110">
          <template #default="{ row }"><span class="mono">{{ row.itemNo }}</span></template>
        </el-table-column>
        <el-table-column prop="billNo" label="所属结算单" width="150">
          <template #default="{ row }"><span class="mono">{{ row.billNo }}</span></template>
        </el-table-column>
        <el-table-column prop="itemName" label="项目" min-width="140" />
        <el-table-column prop="subject" label="科目" min-width="150" />
        <el-table-column label="金额（元）" width="190" align="right">
          <template #default="{ row }">
            <template v-if="editingId === row.id">
              <el-input v-model="editValue" size="small" class="edit-input" placeholder="输入金额" />
              <el-button link type="primary" @click="saveEdit(row)">保存</el-button>
              <el-button link @click="cancelEdit">取消</el-button>
            </template>
            <template v-else>
              <span class="amount mono">{{ row.amount === null ? '—' : fmt(row.amount) }}</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="160" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button v-if="editingId !== row.id" link type="primary" @click="startEdit(row)">调整</el-button>
            <el-button link @click="recap(row)">重算汇总</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pager"
        background
        layout="prev, pager, next"
        :current-page="page"
        :page-size="size"
        :total="total"
        @current-change="onPageChange"
      />

      <div class="summary">
        <div class="sum-item">
          <span class="sum-label">结算单汇总金额合计</span>
          <span class="sum-value mono">{{ fmt(summary.billTotalSum) }}</span>
        </div>
        <div class="sum-item">
          <span class="sum-label">明细条数</span>
          <span class="sum-value mono">{{ summary.detailCount }}</span>
        </div>
        <div class="sum-item">
          <span class="sum-label">资金账户可用合计</span>
          <span class="sum-value mono">{{ fmt(summary.accountAvailable) }}</span>
        </div>
        <div class="sum-item">
          <span class="sum-label">资金账户冻结合计</span>
          <span class="sum-value mono">{{ fmt(summary.accountFrozen) }}</span>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>资金账户</h3>
          <p class="p-sub">共 <b>{{ accounts.length }}</b> 个资金账号</p>
        </div>
      </div>
      <el-table :data="accounts" size="small" border style="width: 100%">
        <el-table-column prop="accountNo" label="资金账号" width="130">
          <template #default="{ row }"><span class="mono">{{ row.accountNo }}</span></template>
        </el-table-column>
        <el-table-column prop="customerName" label="客户名称" min-width="200" />
        <el-table-column label="可用资金（元）" width="160" align="right">
          <template #default="{ row }"><span class="amount mono">{{ fmt(row.available) }}</span></template>
        </el-table-column>
        <el-table-column label="冻结资金（元）" width="160" align="right">
          <template #default="{ row }"><span class="amount mono">{{ fmt(row.frozen) }}</span></template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="160" />
      </el-table>
    </section>

    <el-dialog v-model="dbVisible" title="数据库查询" width="760px">
      <div class="db-bar">
        <el-select v-model="dbTable" size="small" class="db-select">
          <el-option label="settle_bill（结算单汇总）" value="settle_bill" />
          <el-option label="settle_detail（结算明细）" value="settle_detail" />
          <el-option label="fund_account（资金账户）" value="fund_account" />
        </el-select>
        <el-button size="small" type="primary" @click="runQuery">查询</el-button>
        <span class="db-path mono">{{ dbPath }}</span>
      </div>
      <el-table :data="dbRows" size="small" border max-height="360">
        <el-table-column
          v-for="col in dbCols"
          :key="col"
          :prop="col"
          :label="col"
          min-width="130"
        >
          <template #default="{ row }">
            <span class="mono">{{ row[col] === null ? 'NULL' : row[col] }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <div class="result-box">
      <div class="label">操作结果</div>
      <div v-if="!logs.length" class="empty-hint">暂无操作记录</div>
      <div v-else class="logs">
        <div v-for="(l, i) in logs" :key="i" class="log-line">
          <span class="time">{{ l.time }}</span><span>{{ l.text }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '../../utils/http'

const rows = ref([])
const accounts = ref([])
const summary = ref({})
const page = ref(1)
const size = ref(5)
const total = ref(0)
const loading = ref(false)
const editingId = ref(-1)
const editValue = ref('')

const dbVisible = ref(false)
const dbTable = ref('settle_detail')
const dbRows = ref([])
const dbCols = ref([])
const dbPath = ref('')

const logs = ref([])

const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })
function log(text) {
  logs.value.unshift({ time: stamp(), text })
}

const pageCount = computed(() => Math.max(1, Math.ceil(total.value / size.value)))

function fmt(v) {
  if (v === null || v === undefined) return '—'
  const n = Number(v || 0)
  const abs = Math.abs(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return n < 0 ? `(¥${abs})` : `¥${abs}`
}

async function load() {
  loading.value = true
  try {
    const data = await http.get('/dbconsistency/page', { params: { page: page.value, size: size.value } })
    rows.value = data.rows
    accounts.value = data.accounts
    summary.value = data.summary
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function refresh() {
  await load()
  log(`已刷新数据快照 ${summary.value.snapshotAt}，当前第 ${page.value} 页 ${rows.value.length} 条`)
}

function onPageChange(p) {
  page.value = p
  load()
  log(`切换到第 ${p} 页`)
}

function startEdit(row) {
  editingId.value = row.id
  editValue.value = row.amount === null ? '' : String(row.amount)
}

function cancelEdit() {
  editingId.value = -1
  editValue.value = ''
}

async function saveEdit(row) {
  const amount = Number(editValue.value)
  if (Number.isNaN(amount)) return
  const itemNo = row.itemNo
  cancelEdit()
  log(`提交明细 ${itemNo} 金额调整为 ${fmt(amount)}，等待落库…`)
  const res = await http.post('/dbconsistency/detail/update', { id: row.id, amount })
  log(`${res.billNo} 明细已落库：本条 ${fmt(res.amount)}，结算单汇总 ${fmt(res.billTotal)}，明细合计 ${fmt(res.detailSum)}`)
  await load()
}

async function recap(row) {
  const res = await http.post('/dbconsistency/bill/recap', { billNo: row.billNo })
  log(`${res.billNo} 汇总金额已按明细重算为 ${fmt(res.billTotal)}`)
  await load()
}

async function postAccount() {
  const res = await http.post('/dbconsistency/account/post', {})
  log(`清算入账 ${fmt(res.delta)} 已记账到 ${res.accountNo}（${res.updatedAt}），页面数据未自动刷新`)
}

async function openDb() {
  dbVisible.value = true
  const meta = await http.get('/dbconsistency/db/meta')
  dbPath.value = meta.dbPath
  await runQuery()
}

async function runQuery() {
  const res = await http.get('/dbconsistency/db/query', { params: { target: dbTable.value } })
  dbRows.value = res.rows
  dbCols.value = res.count ? Object.keys(res.rows[0]) : []
  log(`数据库查询 ${res.table}，返回 ${res.count} 行原始记录（金额单位：分）`)
}

async function reset() {
  await http.post('/dbconsistency/reset')
  page.value = 1
  cancelEdit()
  await load()
  log('数据库已重建，恢复初始数据')
}

onMounted(async () => {
  await load()
  log(`已加载第 1 页 ${rows.value.length} 条明细，共 ${total.value} 条；结算单汇总合计 ${fmt(summary.value.billTotalSum)}`)
})
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.bar h3 { margin: 0 0 4px; font-size: 15px; font-weight: 600; }
.bar p { margin: 0; }
.bar-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.snap { margin-left: 8px; color: var(--text-3); font-size: 12px; }
.amount { font-variant-numeric: tabular-nums; }
.edit-input { width: 120px; margin-right: 6px; }
.pager { margin-top: 12px; justify-content: flex-end; }
.summary {
  display: flex;
  gap: 32px;
  margin-top: 12px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--paper);
  flex-wrap: wrap;
}
.sum-item { display: flex; flex-direction: column; gap: 4px; }
.sum-label { color: var(--text-3); font-size: 12px; }
.sum-value { font-size: 15px; font-weight: 600; }
.db-bar { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.db-select { width: 220px; }
.db-path { color: var(--text-3); font-size: 12px; }
</style>
