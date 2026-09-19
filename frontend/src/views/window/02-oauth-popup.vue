<template>
  <div class="page">
    <div class="page-title">第三方平台对接</div>
    <p class="page-desc">接入第三方统一授权，授权过程在独立弹出小窗口内完成。</p>

    <section class="panel">
      <h3>渠道平台授权</h3>
      <p class="p-sub">当前登录的是本系统账号，授权后会获得第三方平台的票据能力。</p>

      <div class="auth-card">
        <div class="auth-row">
          <span class="muted">本系统账号</span>
          <b>autotest@demo.cn</b>
        </div>
        <div class="auth-row">
          <span class="muted">目标平台</span>
          <b>渠道数据开放平台</b>
        </div>
        <div class="auth-row">
          <span class="muted">授权状态</span>
          <b v-if="authed" class="text-ok">已授权（{{ authedAt }}）</b>
          <b v-else class="text-err">未授权</b>
        </div>
      </div>

      <div class="toolbar">
        <el-button type="primary" @click="startAuth">发起授权登录</el-button>
        <el-button :disabled="!authed" @click="useTicket">使用授权票据查询</el-button>
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
import { ElMessage } from 'element-plus'

const authed = ref(false)
const authedAt = ref('')
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function onMessage(ev) {
  const data = ev.data || {}
  if (data.type !== 'OAUTH_RESULT') return
  if (data.ok) {
    authed.value = true
    authedAt.value = stamp()
    logs.value.unshift({ time: stamp(), text: '授权窗口已确认：授权成功并自动关闭，主窗口已收到结果' })
    ElMessage.success('授权成功')
  } else {
    logs.value.unshift({ time: stamp(), text: '授权窗口已确认：用户拒绝了授权' })
  }
}

function startAuth() {
  const w = window.open('/iframes/oauth.html', 'oauthWindow', 'width=560,height=560,left=320,top=120')
  logs.value.unshift({
    time: stamp(),
    text: w ? '已打开授权小窗，等待用户在窗口中完成操作' : '授权小窗未能打开（返回 null，可能被浏览器拦截）'
  })
}

function useTicket() {
  logs.value.unshift({ time: stamp(), text: '已使用授权票据拉取渠道数据' })
}

onMounted(() => window.addEventListener('message', onMessage))
onUnmounted(() => window.removeEventListener('message', onMessage))
</script>

<style scoped>
.auth-card {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 18px;
  max-width: 520px;
  background: var(--paper);
}
.auth-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed var(--line-soft);
  font-size: 13px;
}
.auth-row:last-child { border-bottom: 0; }
</style>
