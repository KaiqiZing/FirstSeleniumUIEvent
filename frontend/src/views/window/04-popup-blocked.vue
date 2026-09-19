<template>
  <div class="page">
    <div class="page-title">报表订阅设置</div>
    <p class="page-desc">订阅成功后通过脚本延迟打开预览窗口，浏览器的弹窗策略会影响其能否打开。</p>

    <section class="panel">
      <h3>订阅与预览</h3>
      <p class="p-sub">下方两个入口分别模拟「手势内直接打开」与「延时脚本打开」两种方式。</p>

      <div class="row-form">
        <el-button type="primary" @click="directOpen">立即预览报表（手势内）</el-button>
        <el-button @click="delayedOpen">延时打开预览（脚本触发）</el-button>
      </div>
      <p class="p-sub" style="margin-top: 10px">
        已成功打开预览 {{ openedCount }} 次 / 被拦截 {{ blockedCount }} 次
      </p>
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

const openedCount = ref(0)
const blockedCount = ref(0)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function doOpen(tag) {
  const w = window.open('/iframes/detail.html?id=REPORT-2609', '_blank')
  if (w) {
    openedCount.value += 1
    logs.value.unshift({ time: stamp(), text: `${tag}：预览窗口已打开（成功 ${openedCount.value} 次）` })
  } else {
    blockedCount.value += 1
    logs.value.unshift({ time: stamp(), text: `${tag}：window.open 返回 null，弹出窗口未创建（被拦截 ${blockedCount.value} 次）` })
  }
}

function directOpen() {
  doOpen('立即预览')
}

function delayedOpen() {
  logs.value.unshift({ time: stamp(), text: '已排定延时打开任务（1200ms 后执行），此动作脱离用户手势上下文…' })
  setTimeout(() => doOpen('延时打开'), 1200)
}
</script>
