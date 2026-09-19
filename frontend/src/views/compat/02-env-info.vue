<template>
  <div class="page">
    <div class="page-title">运行环境信息</div>
    <p class="page-desc">读取当前浏览器环境信息，供核对运行与配置环境时使用。</p>

    <section class="panel">
      <h3>浏览器环境</h3>
      <p class="p-sub">以下为只读信息，随浏览器与机器配置不同而不同。</p>
      <el-button size="small" @click="collect">重新采集环境信息</el-button>

      <div class="env-list">
        <div class="kv">
          <span class="k">User Agent</span>
          <span class="v mono">{{ info.ua }}</span>
        </div>
        <div class="kv">
          <span class="k">平台 / 语言</span>
          <span class="v">{{ info.platform }} · {{ info.lang }}</span>
        </div>
        <div class="kv">
          <span class="k">分辨率</span>
          <span class="v">{{ info.screen }}（视口 {{ info.viewport }}）</span>
        </div>
        <div class="kv">
          <span class="k">像素比 devicePixelRatio</span>
          <span class="v mono">{{ info.dpr }}</span>
        </div>
        <div class="kv">
          <span class="k">页面缩放（需浏览器自带）</span>
          <span class="v mono">{{ info.zoomHint }}</span>
        </div>
        <div class="kv">
          <span class="k">时区偏移</span>
          <span class="v">UTC{{ info.tzOffset }}（{{ new Date().toLocaleTimeString('zh-CN', { hour12: false }) }}）</span>
        </div>
        <div class="kv">
          <span class="k">页面状态</span>
          <span class="v">readyState={{ info.ready }} · cookies={{ info.cookieCount }} 项</span>
        </div>
        <div class="kv">
          <span class="k">自动化标识 navigator.webdriver</span>
          <span class="v mono">{{ info.webdriver }}</span>
        </div>
      </div>
    </section>

    <div class="result-box">
      <div class="label">采集记录</div>
      <div v-if="!logs.length" class="empty-hint">暂无采集记录</div>
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

const info = ref({})
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function collect() {
  const dpr = window.devicePixelRatio || 1
  const zoomHint = (dpr * 100).toFixed(0) + '%（等效，受设备缩放影响）'
  info.value = {
    ua: navigator.userAgent,
    platform: navigator.platform || '—',
    lang: navigator.language,
    screen: `${window.screen.width}×${window.screen.height}`,
    viewport: `${window.innerWidth}×${window.innerHeight}`,
    dpr,
    zoomHint,
    tzOffset: -new Date().getTimezoneOffset() / 60 >= 0
      ? '+' + new Date().getTimezoneOffset() / -60
      : String(new Date().getTimezoneOffset() / 60),
    ready: document.readyState,
    cookieCount: document.cookie.split(';').filter(Boolean).length,
    webdriver: typeof navigator.webdriver === 'boolean' ? navigator.webdriver : '未知'
  }
  logs.value.unshift({ time: stamp(), text: '已采集当前浏览器环境信息' })
}

onMounted(collect)
</script>

<style scoped>
.env-list { margin-top: 16px; border: 1px solid var(--border); border-radius: 8px; }
.kv {
  display: flex;
  gap: 18px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--line-soft);
  font-size: 13px;
  align-items: flex-start;
}
.kv:last-child { border-bottom: 0; }
.k { flex: 0 0 230px; color: var(--text-3); }
.v { color: var(--text-1); word-break: break-all; line-height: 1.6; }
</style>
