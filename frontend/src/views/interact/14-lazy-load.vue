<template>
  <div class="page">
    <div class="page-title">任务流水列表</div>
    <p class="page-desc">列表按页从服务端拉取，滚动到容器底部后自动加载下一页。</p>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>任务流水</h3>
          <p class="p-sub">
            已加载 <b>{{ rows.length }}</b> 条 / 共 {{ total }} 条
            <span v-if="loading" class="loading-tip">加载中…</span>
          </p>
        </div>
        <el-button size="small" @click="reset">回到第一页</el-button>
      </div>

      <div ref="scrollRef" class="scroll-box" @scroll="onScroll">
        <div v-for="r in rows" :key="r.id" class="row">
          <span class="row-id mono">{{ r.id }}</span>
          <span class="row-name">{{ r.name }}</span>
          <span class="row-owner">{{ r.owner }}</span>
          <span class="row-status">{{ r.status }}</span>
          <span class="row-amount mono">¥{{ r.amount.toFixed(2) }}</span>
        </div>
        <div v-if="loading" class="more-tip">正在加载下一页…</div>
        <div v-else-if="!hasMore && rows.length" class="more-tip end">已加载全部任务</div>
        <div v-else-if="!rows.length" class="more-tip">暂无数据</div>
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
import { ref, onMounted, onUnmounted } from 'vue'
import http from '../../utils/http'

const scrollRef = ref(null)
const rows = ref([])
const page = ref(0)
const total = ref(0)
const hasMore = ref(true)
const loading = ref(false)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

async function loadNext() {
  if (loading.value || !hasMore.value) return
  loading.value = true
  const next = page.value + 1
  try {
    const data = await http.get('/items', { params: { page: next, size: 10 }, timeout: 15000 })
    rows.value = rows.value.concat(data.list)
    page.value = data.page
    total.value = data.total
    hasMore.value = data.hasMore
    logs.value.unshift({
      time: stamp(),
      text: `已加载第 ${data.page} 页，新增 ${data.list.length} 条，累计 ${rows.value.length} 条`
    })
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

function onScroll() {
  const el = scrollRef.value
  if (!el) return
  if (el.scrollTop + el.clientHeight >= el.scrollHeight - 24) loadNext()
}

function reset() {
  rows.value = []
  page.value = 0
  hasMore.value = true
  logs.value.unshift({ time: stamp(), text: '列表已重置，重新加载第 1 页' })
  loadNext()
}

onMounted(loadNext)
onUnmounted(() => {})
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: flex-start; }
.bar h3 { margin: 0 0 4px; font-size: 15px; }
.bar p { margin: 0; }
.loading-tip { color: var(--warning); margin-left: 8px; font-size: 12px; }
.scroll-box {
  margin-top: 12px;
  height: 360px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: 8px;
}
.row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--line-soft);
  font-size: 13px;
}
.row:last-of-type { border-bottom: 0; }
.row-id { color: var(--text-3); }
.row-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-owner { width: 90px; color: var(--text-3); }
.row-status { width: 70px; }
.row-amount { width: 110px; text-align: right; }
.more-tip {
  text-align: center;
  padding: 12px;
  color: var(--text-3);
  font-size: 12px;
}
.more-tip.end { color: var(--success); }
</style>
