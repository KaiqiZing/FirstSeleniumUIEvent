<template>
  <div class="page">
    <div class="page-title">报销流程处理</div>
    <p class="page-desc">报销入口页面被嵌入在双层框架中，主页面通过消息接收内层的提交结果。</p>

    <section class="panel">
      <h3>报销入口（iframe 内嵌业务）</h3>
      <p class="p-sub">页面下方为主文档内容，上方为内嵌的报销表单入口。</p>

      <div class="frame-shell">
        <iframe
          :key="frameKey"
          :src="frameSrc"
          title="报销入口框架"
          style="width: 100%; height: 560px; border: 0; border-radius: 8px"
        />
      </div>

      <div class="toolbar">
        <el-button @click="reloadFrame">刷新框架页面</el-button>
        <span class="muted" style="font-size: 12px">用于把内层状态恢复到初始</span>
      </div>
    </section>

    <section class="panel" style="margin-bottom: 0">
      <h3>主文档侧边栏信息</h3>
      <p class="p-sub">以下信息与 iframe 内部互不干扰，属于两个独立上下文。</p>
      <div class="row-form">
        <span class="muted">当前处理人：</span><b>运营值班组</b>
        <el-button size="small" @click="logLocal">登记本页处理记录</el-button>
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

const frameKey = ref(0)
const frameSrc = ref('/iframes/frame-a.html')
const logs = ref([])

const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function onMessage(ev) {
  const data = ev.data || {}
  if (data && data.type === 'FRAME_B_SUBMIT') {
    logs.value.unshift({
      time: stamp(),
      text: `主页面已同步到内层提交：单号 ${data.no}，金额 ${data.amount}，事由「${data.reason || '—'}」`
    })
  }
}

function reloadFrame() {
  frameKey.value += 1
  frameSrc.value = `/iframes/frame-a.html?v=${Date.now()}`
  logs.value.unshift({ time: stamp(), text: '已重新加载内嵌报销入口框架' })
}

function logLocal() {
  logs.value.unshift({ time: stamp(), text: '主文档记录：登记了本页处理记录' })
}

onMounted(() => window.addEventListener('message', onMessage))
onUnmounted(() => window.removeEventListener('message', onMessage))
</script>

<style scoped>
.frame-shell {
  border: 1px dashed var(--brand-line);
  border-radius: 8px;
  padding: 6px;
  background: var(--brand-soft);
}
</style>
