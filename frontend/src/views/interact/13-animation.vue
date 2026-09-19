<template>
  <div class="page">
    <div class="page-title">公告推送中心</div>
    <p class="page-desc">推送面板以渐入+位移动画入场，动画结束前部分操作不稳定。</p>

    <section class="panel">
      <h3>进行中的推送</h3>
      <p class="p-sub">点击打开最新的推送面板查看详情。</p>
      <el-button type="primary" @click="openPanel">打开最新推送</el-button>
    </section>

    <section v-if="open" class="panel slide-panel" :class="{ entered: !animating }" @animationend="onAnimEnd">
      <div class="push-head">
        <div>
          <h3 style="margin: 0">系统升级公告（批次 20260903）</h3>
          <p class="p-sub" style="margin: 4px 0 0">运营后台将于 9 月 12 日 22:00-24:00 进行升级维护</p>
        </div>
        <el-tag v-if="animating" type="warning" size="small">渲染中…</el-tag>
        <el-tag v-else type="success" size="small">已就绪</el-tag>
      </div>
      <p class="push-body">
        本次升级包含报表引擎、批量导出与权限模块的优化，期间可能导致个别页面短暂不可用。
        请各业务线提前完成当日数据归档，并在升级完成后验证关键流程。
      </p>
      <div class="toolbar">
        <el-button type="primary" @click="confirmRead">我知道了</el-button>
        <el-button @click="closePanel">稍后处理</el-button>
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
import { ref } from 'vue'

const open = ref(false)
const animating = ref(false)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function openPanel() {
  open.value = true
  animating.value = true
  logs.value.unshift({ time: stamp(), text: '推送面板已打开，内容开始渐入' })
}

function onAnimEnd(ev) {
  if (ev && ev.animationName !== 'panel-in') return
  animating.value = false
  logs.value.unshift({ time: stamp(), text: '推送面板动画完成，内容就绪' })
}

function confirmRead() {
  logs.value.unshift({ time: stamp(), text: '已确认阅读系统升级公告' })
}

function closePanel() {
  open.value = false
  logs.value.unshift({ time: stamp(), text: '已关闭推送面板（稍后处理）' })
}
</script>

<style scoped>
.slide-panel {
  animation: panel-in 2.4s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
  transform-origin: top center;
}
.slide-panel.entered { animation: none; transform: none; }
@keyframes panel-in {
  0% { opacity: 0.1; transform: translateY(46px) scale(0.97); }
  70% { opacity: 0.6; transform: translateY(8px) scale(0.995); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}
.push-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.push-body { color: var(--text-2); line-height: 1.9; font-size: 13px; margin: 12px 0; }
</style>
