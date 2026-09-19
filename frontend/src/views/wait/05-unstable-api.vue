<template>
  <div class="page">
    <div class="page-title">渠道数据同步</div>
    <p class="page-desc">同步服务响应不稳定：可能直接失败，也可能等待较长时间后成功。</p>

    <section class="panel">
      <h3>同步任务</h3>
      <p class="p-sub">同步过程偶发失败，页面上提供重试入口。</p>

      <div class="row-form">
        <el-button type="primary" :loading="loading" @click="doSync">同步渠道数据</el-button>
        <el-button :disabled="loading || !attempts" @click="doSync">重试一次</el-button>
        <span class="muted" style="font-size: 12px">
          本次会话已尝试 {{ attempts }} 次，成功 {{ okCount }} 次
        </span>
      </div>

      <div v-if="rows.length" class="sync-result">
        <div class="sync-head">本次同步到的渠道</div>
        <el-table :data="rows" size="small" border style="width: 100%">
          <el-table-column prop="id" label="渠道编号" width="110" />
          <el-table-column prop="name" label="渠道名称" min-width="180" />
          <el-table-column prop="created" label="同步时刻" width="110" />
        </el-table>
      </div>
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

const loading = ref(false)
const rows = ref([])
const attempts = ref(0)
const okCount = ref(0)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

async function doSync() {
  if (loading.value) return
  loading.value = true
  attempts.value += 1
  const start = Date.now()
  logs.value.unshift({ time: stamp(), text: `第 ${attempts.value} 次发起同步请求…` })
  try {
    const data = await http.get('/unstable', { timeout: 20000 })
    rows.value = data.rows
    okCount.value += 1
    logs.value.unshift({
      time: stamp(),
      text: `同步成功：返回 ${data.rows.length} 条渠道数据，耗时 ${((Date.now() - start) / 1000).toFixed(1)}s`
    })
  } catch (err) {
    console.error(err)
    logs.value.unshift({ time: stamp(), text: `第 ${attempts.value} 次同步失败，接口异常或超时`, err: true })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.sync-result { margin-top: 16px; border: 1px solid var(--border); border-radius: 8px; padding: 12px; }
.sync-head { font-size: 13px; font-weight: 600; margin-bottom: 10px; color: var(--text-2); }
</style>
