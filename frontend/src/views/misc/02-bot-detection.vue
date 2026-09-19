<template>
  <div class="page">
    <div class="page-title">渠道数据摘要</div>
    <p class="page-desc">生成摘要前会做一次访问环境校验，校验结果影响摘要生成是否可用。</p>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>数据摘要生成</h3>
          <p class="p-sub">环境校验完成后可生成当日渠道数据摘要。</p>
        </div>
        <el-tag :type="checked ? (passed ? 'success' : 'danger') : 'info'" effect="light">
          {{ checked ? (passed ? '环境校验通过' : '环境校验未通过') : '待校验' }}
        </el-tag>
      </div>

      <div class="detect-card">
        <div class="kv"><span>访问标识</span><b class="mono">{{ detectMark }}</b></div>
        <div class="kv"><span>判定结果</span><b>{{ checked ? (passed ? '正常浏览器环境' : '检测到自动化特征，能力受限') : '尚未执行校验' }}</b></div>
      </div>

      <div class="toolbar">
        <el-button type="primary" @click="runCheck">执行环境校验</el-button>
        <el-button type="success" plain :disabled="!passed" @click="genSummary">生成当日数据摘要</el-button>
      </div>

      <div v-if="blockedHint" class="block-tip">
        <el-icon><WarningFilled /></el-icon>
        <span>操作受限：当前访问环境未能通过校验，请联系客服通过人工通道处理。</span>
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
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'

const detectMark = ref('')
const checked = ref(false)
const passed = ref(false)
const blockedHint = ref(false)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function runCheck() {
  detectMark.value = String(navigator.webdriver)
  passed.value = !navigator.webdriver
  checked.value = true
  logs.value.unshift({
    time: stamp(),
    text: `环境校验完成：标识 ${detectMark.value}，判定 ${passed.value ? '通过' : '不通过'}`
  })
}

function genSummary() {
  if (!passed.value) return
  logs.value.unshift({ time: stamp(), text: '当日渠道数据摘要已生成' })
  ElMessage.success('摘要已生成')
  blockedHint.value = false
}

function isLimited() {
  // 保留业务提示逻辑：受限时统一展示引导
  blockedHint.value = checked.value && !passed.value
}

runCheck()
setTimeout(isLimited, 300)
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.bar h3 { margin: 0 0 4px; font-size: 15px; }
.bar p { margin: 0; }
.detect-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 16px;
  background: var(--paper);
  margin-bottom: 14px;
  max-width: 460px;
}
.kv { display: flex; justify-content: space-between; padding: 8px 0; font-size: 13px; border-bottom: 1px dashed var(--line-soft); }
.kv:last-child { border-bottom: 0; }
.kv span { color: var(--text-3); }
.block-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--danger);
  background: #fbeff0;
  border: 1px solid #f0c9c6;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 13px;
  margin-top: 4px;
}
</style>
