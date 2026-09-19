<template>
  <div class="page">
    <div class="page-title">汇总台账</div>
    <p class="page-desc">台账组件由前端框架组件封装渲染，内部结构位于组件的影子子树中。</p>

    <section class="panel">
      <h3>汇总台账组件</h3>
      <p class="p-sub">请先尝试在表单内输入并保存，再执行内层子任务。</p>
      <div ref="hostWrap">
        <shadow-demo-box id="shadowBox"></shadow-demo-box>
      </div>
      <div class="toolbar">
        <el-button @click="readShadow">读取影子节点状态</el-button>
        <span class="muted" style="font-size: 12px">通过脚本穿透读取组件内部状态</span>
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

const hostWrap = ref(null)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function push(text) {
  logs.value.unshift({ time: stamp(), text })
}

function onShadow(ev) {
  if (ev.type === 'shadow-outer-done') {
    push(`影子外层已保存，内容「${ev.detail?.value || '（空）'}」`)
  } else if (ev.type === 'shadow-inner-done') {
    push('影子内层子任务已执行完成')
  }
}

function readShadow() {
  const box = document.getElementById('shadowBox')
  if (!box || !box.shadowRoot) {
    push('未找到组件或其影子根')
    return
  }
  const st = box.shadowRoot.querySelector('.sst')
  push(`穿透读取外层：${st ? st.textContent.trim() : '—'}`)
  const inner = box.shadowRoot.querySelector('shadow-inner-box')
  if (inner && inner.shadowRoot) {
    const ist = inner.shadowRoot.querySelector('.sst')
    push(`穿透读取内层：${ist ? ist.textContent.trim() : '—'}`)
  }
}

onMounted(() => {
  hostWrap.value?.addEventListener('shadow-outer-done', onShadow)
  hostWrap.value?.addEventListener('shadow-inner-done', onShadow)
})
onUnmounted(() => {
  hostWrap.value?.removeEventListener('shadow-outer-done', onShadow)
  hostWrap.value?.removeEventListener('shadow-inner-done', onShadow)
})
</script>
