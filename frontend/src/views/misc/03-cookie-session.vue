<template>
  <div class="page">
    <div class="page-title">渠道运营工作台</div>
    <p class="page-desc">登录态保存在会话中，刷新页面、重开标签甚至重开浏览器都依赖会话 Cookie 是否还在。</p>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>登录状态</h3>
          <p class="p-sub">当前登录用户：
            <template v-if="user"><b>{{ user.name }}</b><span class="muted">（{{ user.account }} · {{ user.role }}）</span></template>
            <template v-else><b>未登录</b></template>
          </p>
        </div>
        <el-tag :type="user ? 'success' : 'info'" size="large">
          {{ user ? '已登录' : '未登录' }}
        </el-tag>
      </div>
    </section>

    <section v-if="!user" class="panel">
      <h3>账号登录</h3>
      <p class="p-sub">可使用内置账号 tester / demo 登录（密码任意非空）。</p>
      <div class="row-form">
        <div class="fld">
          <span class="f-label">账号</span>
          <el-input v-model="account" placeholder="tester 或 demo" style="width: 220px" />
        </div>
        <div class="fld">
          <span class="f-label">密码</span>
          <el-input v-model="password" type="password" placeholder="请输入密码" style="width: 220px" show-password />
        </div>
        <el-checkbox v-model="remember">记住登录状态</el-checkbox>
        <el-button type="primary" :loading="busy" @click="doLogin">登录</el-button>
      </div>
    </section>

    <section v-else class="panel">
      <h3>工作台能力</h3>
      <p class="p-sub">已登录状态下可使用下方操作。</p>
      <div class="toolbar">
        <el-button type="primary" @click="doBiz">生成当日运营快照</el-button>
        <el-button @click="refreshMe">重新检测登录态</el-button>
        <el-button type="danger" plain @click="doLogout">退出登录</el-button>
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../utils/http'

const user = ref(null)
const account = ref('tester')
const password = ref('')
const remember = ref(false)
const busy = ref(false)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

async function refreshMe() {
  try {
    const data = await http.get('/auth/me', { timeout: 10000 })
    user.value = data || null
    logs.value.unshift({
      time: stamp(),
      text: user.value ? `登录态检测：已登录（${user.value.account}）` : '登录态检测：未登录（会话缺失或已过期）'
    })
  } catch (err) {
    console.error(err)
  }
}

async function doLogin() {
  if (!account.value || !password.value) {
    ElMessage.warning('请输入账号与密码')
    return
  }
  busy.value = true
  try {
    const data = await http.post('/auth/login', { account: account.value, password: password.value, remember: remember.value })
    user.value = data.user
    logs.value.unshift({ time: stamp(), text: `登录成功：${data.user.name}（记住状态：${data.remember ? '是' : '否'}）` })
    ElMessage.success('登录成功')
  } catch (err) {
    console.error(err)
  } finally {
    busy.value = false
  }
}

async function doLogout() {
  await http.post('/auth/logout', {})
  user.value = null
  logs.value.unshift({ time: stamp(), text: '已退出登录，会话 Cookie 已清除' })
}

function doBiz() {
  logs.value.unshift({ time: stamp(), text: '已生成当日运营快照（需要登录态）' })
}

onMounted(refreshMe)
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: flex-start; }
.bar h3 { margin: 0 0 6px; font-size: 15px; }
.bar p { margin: 0; }
</style>
