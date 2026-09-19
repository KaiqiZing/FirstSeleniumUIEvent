<template>
  <div class="page">
    <div class="page-title">结算单金额勾稽</div>
    <p class="page-desc">按结算批次展示父级结算单，展开后显示子级明细；系统按子单金额合计与父单申报金额勾稽。</p>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>结算单列表</h3>
          <p class="p-sub">
            父单 <b>{{ parents.length }}</b> 张 / 子单 {{ childCount }} 条
            <span v-if="recalcId" class="loading-tip">正在重算 {{ recalcId }} …</span>
          </p>
        </div>
        <div class="bar-actions">
          <el-button size="small" @click="expandAll(true)">展开全部</el-button>
          <el-button size="small" @click="expandAll(false)">收起全部</el-button>
          <el-button size="small" @click="reset">重置数据</el-button>
        </div>
      </div>

      <el-table
        :data="parents"
        row-key="id"
        :tree-props="{ children: 'children' }"
        :expand-row-keys="expandedKeys"
        size="small"
        border
        style="width: 100%"
        @expand-change="onExpandChange"
      >
        <el-table-column label="结算单号 / 明细编号" min-width="200">
          <template #default="{ row }"><span class="mono">{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column label="客户 / 明细项目" min-width="180">
          <template #default="{ row }"><span>{{ row.children ? row.customer : row.name }}</span></template>
        </el-table-column>
        <el-table-column label="业务类型 / 科目" min-width="150">
          <template #default="{ row }"><span>{{ row.children ? row.bizType : row.subject }}</span></template>
        </el-table-column>
        <el-table-column label="金额" min-width="150" align="right">
          <template #default="{ row }">
            <span class="amount mono">{{ fmt(row.children ? row.declaredAmount : row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="勾稽状态" min-width="230">
          <template #default="{ row }">
            <template v-if="row.children">
              <span v-if="row.state === 'matched'" class="tag ok">金额一致</span>
              <span v-else class="tag bad">差异 {{ fmt(row.diff) }}</span>
              <span class="sub">子单合计 {{ fmt(row.childTotal) }}</span>
            </template>
            <template v-else>
              <el-button v-if="editingId !== row.id" link type="primary" @click="startEdit(row)">调整</el-button>
              <template v-else>
                <el-input v-model="editValue" size="small" class="edit-input" placeholder="输入金额" />
                <el-button link type="primary" @click="saveEdit(row)">保存</el-button>
                <el-button link @click="cancelEdit">取消</el-button>
              </template>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="summary">
        <div class="sum-item">
          <span class="sum-label">子单金额合计</span>
          <span class="sum-value mono">{{ fmt(total.child) }}</span>
        </div>
        <div class="sum-item">
          <span class="sum-label">父单申报合计</span>
          <span class="sum-value mono">{{ fmt(total.declared) }}</span>
        </div>
        <div class="sum-item">
          <span class="sum-label">勾稽差额</span>
          <span class="sum-value mono" :class="Math.abs(total.diff) < 0.005 ? 'ok-text' : 'bad-text'">{{ fmt(total.diff) }}</span>
        </div>
      </div>
    </section>

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

const parents = ref([])
const expandedKeys = ref([])
const editingId = ref('')
const editValue = ref('')
const recalcId = ref('')
const logs = ref([])

const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })
function log(text) {
  logs.value.unshift({ time: stamp(), text })
}

// 金融报表常见格式：千分位 + 负数用括号表示
function fmt(v) {
  const n = Number(v || 0)
  const abs = Math.abs(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return n < 0 ? `(¥${abs})` : `¥${abs}`
}

const childCount = computed(() =>
  parents.value.reduce((s, p) => s + (p.children ? p.children.length : 0), 0)
)

const total = computed(() => {
  let child = 0
  let declared = 0
  parents.value.forEach((p) => {
    declared += Number(p.declaredAmount || 0)
    ;(p.children || []).forEach((c) => {
      child += Number(c.amount || 0)
    })
  })
  child = Math.round(child * 100) / 100
  declared = Math.round(declared * 100) / 100
  return { child, declared, diff: Math.round((child - declared) * 100) / 100 }
})

async function load() {
  const data = await http.get('/settlement/list')
  parents.value = data.parents
}

function expandAll(flag) {
  expandedKeys.value = flag ? parents.value.map((p) => p.id) : []
  log(flag ? `已展开全部父级结算单（共 ${parents.value.length} 张）` : '已收起全部父级结算单')
}

function onExpandChange(row, expanded) {
  if (expanded) {
    if (!expandedKeys.value.includes(row.id)) expandedKeys.value = expandedKeys.value.concat(row.id)
  } else {
    expandedKeys.value = expandedKeys.value.filter((k) => k !== row.id)
  }
  log(`${expanded ? '展开' : '收起'} 父级结算单 ${row.id}（${row.customer}）`)
}

function startEdit(row) {
  editingId.value = row.id
  editValue.value = String(row.amount)
}

function cancelEdit() {
  editingId.value = ''
  editValue.value = ''
}

async function saveEdit(row) {
  const parent = parents.value.find((p) => (p.children || []).some((c) => c.id === row.id))
  if (!parent) return
  const amount = Number(editValue.value)
  if (Number.isNaN(amount)) return
  const items = parent.children.map((c) => ({ id: c.id, amount: c.id === row.id ? amount : c.amount }))

  cancelEdit()
  recalcId.value = parent.id
  log(`提交子单 ${row.id} 金额调整为 ${fmt(amount)}，等待后台重算…`)
  try {
    const res = await http.post('/settlement/recalc', { parentId: parent.id, items })
    const target = parents.value.find((p) => p.id === res.parentId)
    if (target) {
      const hit = target.children.find((c) => c.id === row.id)
      if (hit) hit.amount = amount
      target.childTotal = res.childTotal
      target.diff = res.diff
      target.state = res.state
    }
    log(
      `${res.parentId} 重算完成：子单合计 ${fmt(res.childTotal)}，申报 ${fmt(res.declaredAmount)}，差额 ${fmt(res.diff)}（${res.state === 'matched' ? '金额一致' : '存在差异'}）`
    )
  } catch (err) {
    console.error(err)
  } finally {
    recalcId.value = ''
  }
}

async function reset() {
  await http.post('/settlement/reset')
  expandedKeys.value = []
  cancelEdit()
  await load()
  log('结算数据已重置为初始状态')
}

onMounted(async () => {
  await load()
  log(`已加载 ${parents.value.length} 张父级结算单，子单默认折叠未渲染`)
})
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.bar h3 { margin: 0 0 4px; font-size: 15px; font-weight: 600; }
.bar p { margin: 0; }
.bar-actions { display: flex; gap: 8px; }
.loading-tip { color: var(--warning); margin-left: 8px; font-size: 12px; }
.amount { font-variant-numeric: tabular-nums; }
.tag { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 12px; }
.tag.ok { background: #eef6ef; color: var(--success); border: 1px solid #b9dcc4; }
.tag.bad { background: #fbeff0; color: var(--danger); border: 1px solid #f0c9c6; }
.sub { margin-left: 8px; color: var(--text-3); font-size: 12px; }
.edit-input { width: 110px; margin-right: 6px; }
.summary {
  display: flex;
  gap: 32px;
  margin-top: 12px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--paper);
}
.sum-item { display: flex; flex-direction: column; gap: 4px; }
.sum-label { color: var(--text-3); font-size: 12px; }
.sum-value { font-size: 15px; font-weight: 600; }
.ok-text { color: var(--success); }
.bad-text { color: var(--danger); }
</style>
