<template>
  <div class="page">
    <div class="page-title">渠道后台登录</div>
    <p class="page-desc">登录表单附加图形验证码校验，验证码图片由服务端动态生成。</p>

    <section class="panel">
      <h3>登录</h3>
      <p class="p-sub">输入账号密码后，再填写图片中的验证码完成登录。</p>

      <div class="login-form">
        <div class="fld">
          <span class="f-label">账号</span>
          <el-input v-model="account" placeholder="请输入渠道账号" />
        </div>
        <div class="fld">
          <span class="f-label">密码</span>
          <el-input v-model="password" type="password" placeholder="请输入登录密码" show-password />
        </div>
        <div class="fld">
          <span class="f-label">验证码</span>
          <div class="captcha-row">
            <el-input v-model="captcha" placeholder="请输入验证码" style="width: 180px" maxlength="6" />
            <img v-if="captchaImg" :src="captchaImg" alt="验证码" class="cap-img" title="点击刷新验证码" @click="loadCaptcha" />
            <el-button link type="primary" @click="loadCaptcha">看不清，换一张</el-button>
          </div>
        </div>
        <div class="toolbar">
          <el-button type="primary" :loading="submitting" @click="doLogin">登 录</el-button>
        </div>
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

const account = ref('')
const password = ref('')
const captcha = ref('')
const captchaImg = ref('')
const captchaSid = ref('')
const submitting = ref(false)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

async function loadCaptcha() {
  try {
    const data = await http.get('/captcha', { timeout: 10000 })
    captchaSid.value = data.sid
    captchaImg.value = data.image
    captcha.value = ''
  } catch (err) {
    console.error(err)
  }
}

async function doLogin() {
  if (!account.value || !password.value) {
    ElMessage.warning('请输入账号与密码')
    return
  }
  if (!captcha.value.trim()) {
    ElMessage.warning('请输入验证码')
    return
  }
  submitting.value = true
  try {
    await http.post('/captcha/verify', { sid: captchaSid.value, code: captcha.value }, { timeout: 10000 })
    logs.value.unshift({ time: stamp(), text: `验证码校验通过，账号「${account.value}」登录成功` })
    ElMessage.success('登录成功')
    loadCaptcha()
  } catch (err) {
    console.error(err)
    logs.value.unshift({ time: stamp(), text: '登录失败：验证码校验未通过', err: true })
    loadCaptcha()
  } finally {
    submitting.value = false
  }
}

onMounted(loadCaptcha)
</script>

<style scoped>
.login-form { max-width: 460px; display: flex; flex-direction: column; gap: 14px; }
.fld { display: flex; flex-direction: column; gap: 6px; }
.f-label { font-size: 12px; color: var(--text-3); }
.captcha-row { display: flex; align-items: center; gap: 12px; }
.cap-img {
  height: 34px;
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
}
</style>
