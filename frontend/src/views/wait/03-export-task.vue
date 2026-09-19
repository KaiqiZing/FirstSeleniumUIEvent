<template>
  <div class="page">
    <div class="page-title">对账单批量导出</div>
    <p class="page-desc">导出由服务端异步执行，需要轮询任务进度，完成后可下载文件。</p>

    <section class="panel">
      <h3>导出中心</h3>
      <p class="p-sub">选择导出范围后发起导出，服务端将分批生成结果文件。</p>

      <div class="row-form">
        <div class="fld">
          <span class="f-label">导出范围</span>
          <el-select v-model="range" style="width: 220px">
            <el-option label="2026 年 8 月全量对账单" value="2026-08" />
            <el-option label="本季度渠道返利单" value="q3" />
            <el-option label="近 30 天售后单" value="after" />
          </el-select>
        </div>
        <el-button type="primary" :disabled="!!task" @click="startExport">发起导出</el-button>
      </div>

      <template v-if="task">
        <div class="task-box">
          <div class="task-head">
            <span class="mono">任务号：{{ task.taskId }}</span>
            <el-tag v-if="!task.done" type="warning" size="small">处理中</el-tag>
            <el-tag v-else type="success" size="small">已完成</el-tag>
          </div>
          <el-progress :percentage="task.progress" :stroke-width="14" :status="task.done ? 'success' : undefined" />
          <div class="toolbar" style="margin-top: 12px">
            <a v-if="task.done" :href="`/api/export/file/${task.taskId}`" class="dl-link" @click="logDownload">
              <el-button type="success">下载导出文件</el-button>
            </a>
          </div>
        </div>
      </template>
      <div v-else class="empty-hint" style="margin-top: 10px">暂无进行中的导出任务</div>
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
import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../utils/http'

const range = ref('2026-08')
const task = ref(null)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })
let poller = null

async function startExport() {
  const data = await http.post('/export/start', { range: range.value }, { timeout: 10000 })
  task.value = { taskId: data.task_id, progress: 0, done: false }
  logs.value.unshift({ time: stamp(), text: `导出任务已发起，任务号 ${data.task_id}` })
  poll()
}

async function poll() {
  if (!task.value || task.value.done) return
  clearTimeout(poller)
  try {
    const st = await http.get(`/export/status/${task.value.taskId}`, { timeout: 12000 })
    task.value.progress = st.progress
    if (st.state === 'done') {
      task.value.done = true
      logs.value.unshift({ time: stamp(), text: `导出完成：任务 ${task.value.taskId} 进度 100%` })
      ElMessage.success('导出完成，可下载文件')
      return
    }
    if (st.state === 'error') {
      task.value.done = true
      logs.value.unshift({ time: stamp(), text: '导出任务处理失败，请重新发起' })
      return
    }
    poller = setTimeout(poll, 1000)
  } catch (err) {
    console.error(err)
    poller = setTimeout(poll, 1500)
  }
}

function logDownload() {
  logs.value.unshift({ time: stamp(), text: '已触发下载导出文件' })
}

onUnmounted(() => clearTimeout(poller))
</script>

<style scoped>
.task-box {
  margin-top: 16px;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  background: var(--paper);
}
.task-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.dl-link { text-decoration: none; }
</style>
