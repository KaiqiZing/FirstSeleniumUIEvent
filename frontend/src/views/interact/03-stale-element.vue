<template>
  <div class="page">
    <div class="page-title">任务看板</div>
    <p class="page-desc">看板数据会周期性重建刷新，面板元素会被整体替换。可关闭自动刷新后手动刷新。</p>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>进行中的任务</h3>
          <p class="p-sub">已刷新 <b>{{ refreshCount }}</b> 次 · 最近刷新 {{ lastRefresh || '—' }}</p>
        </div>
        <div class="bar-actions">
          <el-switch v-model="autoRefresh" active-text="自动刷新" style="margin-right: 14px" />
          <el-button :disabled="autoRefresh" @click="refresh">手动刷新</el-button>
        </div>
      </div>

      <el-table :data="list" size="small" border style="width: 100%">
        <el-table-column prop="id" label="任务编号" width="200" />
        <el-table-column prop="name" label="任务名称" min-width="180" />
        <el-table-column prop="owner" label="负责人" width="120" />
        <el-table-column prop="state" label="状态" width="110" />
        <el-table-column label="操作" width="110">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewRow(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
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
import { ref, onMounted, onUnmounted, watch } from 'vue'

const POOL = [
  { id: 'T-1001', name: '接口联调任务', owner: '张工', state: '进行中' },
  { id: 'T-1002', name: '数据迁移核对', owner: '李工', state: '待审阅' },
  { id: 'T-1003', name: '回归测试执行', owner: '王工', state: '进行中' },
  { id: 'T-1004', name: '埋点验收', owner: '赵工', state: '已完成' },
  { id: 'T-1005', name: '发布文档整理', owner: '陈工', state: '已暂停' },
  { id: 'T-1006', name: '环境巡检', owner: '刘工', state: '进行中' }
]

const list = ref([])
const refreshCount = ref(0)
const lastRefresh = ref('')
const autoRefresh = ref(false)
const logs = ref([])
let seq = 0
let timer = null

const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function buildRows() {
  const shuffled = [...POOL].sort(() => Math.random() - 0.5)
  return shuffled.map((r) => ({ ...r, id: r.id + '-' + String(seq++).padStart(3, '0') }))
}

function refresh() {
  // 重建整份数据，key 全部变化 -> DOM 节点被整体替换，旧引用失效
  list.value = buildRows()
  refreshCount.value += 1
  lastRefresh.value = stamp()
}

function viewRow(row) {
  logs.value.unshift({ time: stamp(), text: `已查看任务「${row.name}」（编号 ${row.id}）` })
}

watch(autoRefresh, (on) => {
  clearInterval(timer)
  if (on) timer = setInterval(refresh, 5000)
})

onMounted(() => {
  refresh()
  if (autoRefresh.value) timer = setInterval(refresh, 5000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.bar h3 { margin: 0 0 4px; font-size: 15px; font-weight: 600; }
.bar p { margin: 0; }
.bar-actions { display: flex; align-items: center; }
</style>
