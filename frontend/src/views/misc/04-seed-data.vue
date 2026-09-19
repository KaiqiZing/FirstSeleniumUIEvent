<template>
  <div class="page">
    <div class="page-title">临时工单管理</div>
    <p class="page-desc">工单编号由服务端即时生成（每次唯一），生成后可归档到本地列表，也可查询服务端全部已生成数据。</p>

    <section class="panel">
      <h3>生成临时工单</h3>
      <p class="p-sub">填入业务名称后生成一条带时间戳后缀的唯一工单数据。</p>
      <div class="row-form">
        <div class="fld">
          <span class="f-label">业务名称</span>
          <el-input v-model="bizName" placeholder="如：退款复核 / 促销对账" style="width: 260px" />
        </div>
        <el-button type="primary" :loading="generating" @click="generate">生成工单编号</el-button>
      </div>

      <div v-if="record" class="gen-result">
        <div class="gen-line"><span>工单编号</span><b class="mono">{{ record.id }}</b></div>
        <div class="gen-line"><span>业务名称</span><b>{{ record.name }}</b></div>
        <div class="gen-line"><span>生成时刻</span><b>{{ record.created }}</b></div>
        <div class="toolbar" style="margin-top: 10px">
          <el-button type="success" size="small" @click="archive">归档此工单</el-button>
          <el-button size="small" @click="loadAll">查询服务端已生成数据</el-button>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>归档列表</h3>
          <p class="p-sub">本页面已归档 {{ archives.length }} 条</p>
        </div>
        <div class="muted" style="font-size: 12px">服务端累计生成 {{ remoteCount }} 条</div>
      </div>
      <div v-if="archives.length" class="rec-list">
        <div v-for="r in archives" :key="r.id" class="rec">
          <span class="mono rec-id">{{ r.id }}</span>
          <span class="rec-text">{{ r.name }}</span>
        </div>
      </div>
      <div v-else class="empty-hint" style="text-align: center; padding: 16px">暂无归档工单</div>
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../utils/http'

const bizName = ref('')
const generating = ref(false)
const record = ref(null)
const archives = ref([])
const remoteCount = ref(0)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

async function generate() {
  if (!bizName.value.trim()) {
    ElMessage.warning('请输入业务名称')
    return
  }
  generating.value = true
  try {
    const data = await http.post('/seed/new', { name: bizName.value }, { timeout: 10000 })
    record.value = data
    logs.value.unshift({ time: stamp(), text: `服务端已生成工单：${data.id}（${data.name}）` })
  } catch (err) {
    console.error(err)
  } finally {
    generating.value = false
  }
}

function archive() {
  if (!record.value) return
  archives.value.unshift({ id: record.value.id, name: record.value.name })
  logs.value.unshift({ time: stamp(), text: `工单已归档：${record.value.id}` })
}

async function loadAll() {
  const data = await http.get('/seed/list', { timeout: 10000 })
  remoteCount.value = data.records.length
  logs.value.unshift({ time: stamp(), text: `查询服务端已生成数据：共 ${data.records.length} 条` })
}

onMounted(loadAll)
</script>

<style scoped>
.gen-result {
  margin-top: 14px;
  max-width: 560px;
  border: 1px solid var(--brand-line);
  background: var(--brand-soft);
  border-radius: 10px;
  padding: 12px 16px;
}
.gen-line { display: flex; gap: 12px; padding: 5px 0; font-size: 13px; }
.gen-line span { color: var(--text-3); width: 90px; }
.bar { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.bar h3 { margin: 0 0 4px; font-size: 15px; }
.bar p { margin: 0; }
.rec-list { border: 1px solid var(--border); border-radius: 8px; }
.rec { display: flex; gap: 12px; padding: 10px 14px; border-bottom: 1px solid var(--line-soft); font-size: 13px; }
.rec:last-child { border-bottom: 0; }
.rec-id { color: var(--text-3); }
.rec-text { flex: 1; }
</style>
