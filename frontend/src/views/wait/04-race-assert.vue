<template>
  <div class="page">
    <div class="page-title">处理记录登记</div>
    <p class="page-desc">保存请求需要一段时间完成落库，保存后列表数据会延后才可查询到。</p>

    <section class="panel">
      <h3>登记处理记录</h3>
      <p class="p-sub">提交内容后，可在下方列表按需刷新查看。</p>
      <div class="row-form">
        <div class="fld" style="flex: 1">
          <span class="f-label">处理内容</span>
          <el-input v-model="content" placeholder="请输入本次处理内容" maxlength="30" />
        </div>
        <el-button type="primary" :loading="saving" @click="saveRecord">保存</el-button>
      </div>
    </section>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>已登记记录</h3>
          <p class="p-sub">当前共 <b>{{ records.length }}</b> 条，最后查询 {{ lastQuery || '—' }}</p>
        </div>
        <el-button size="small" @click="loadList">刷新已存记录</el-button>
      </div>
      <div v-if="records.length" class="rec-list">
        <div v-for="r in records" :key="r.id" class="rec">
          <span class="mono rec-id">{{ r.id }}</span>
          <span class="rec-text">{{ r.remark }}</span>
          <span class="muted">{{ r.created }}</span>
        </div>
      </div>
      <div v-else class="empty-hint" style="padding: 20px 0; text-align: center">
        尚未查询到已保存记录
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../utils/http'

const content = ref('')
const saving = ref(false)
const records = ref([])
const lastQuery = ref('')
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

async function saveRecord() {
  if (!content.value.trim()) {
    ElMessage.warning('请输入处理内容')
    return
  }
  if (saving.value) return
  saving.value = true
  const start = Date.now()
  logs.value.unshift({ time: stamp(), text: `已提交保存请求：「${content.value.trim()}」…` })
  try {
    const rec = await http.post('/race/save', { remark: content.value }, { timeout: 15000 })
    logs.value.unshift({
      time: stamp(),
      text: `保存请求完成：单号 ${rec.id}，落库耗时 ${((Date.now() - start) / 1000).toFixed(1)}s`
    })
    content.value = ''
  } catch (err) {
    console.error(err)
  } finally {
    saving.value = false
  }
}

async function loadList() {
  const data = await http.get('/race/list', { timeout: 10000 })
  records.value = data.records
  lastQuery.value = stamp()
  logs.value.unshift({ time: stamp(), text: `已刷新列表：当前 ${data.records.length} 条记录` })
}

onMounted(loadList)
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.bar h3 { margin: 0 0 4px; font-size: 15px; }
.bar p { margin: 0; }
.rec-list { border: 1px solid var(--border); border-radius: 8px; }
.rec {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--line-soft);
  font-size: 13px;
}
.rec:last-child { border-bottom: 0; }
.rec-id { color: var(--text-3); }
.rec-text { flex: 1; }
</style>
