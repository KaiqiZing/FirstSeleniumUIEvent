<template>
  <div class="page">
    <div class="page-title">活动档期排期</div>
    <p class="page-desc">排期表单使用浏览器原生日期与时间控件，不同浏览器对其操作方式差异明显。</p>

    <section class="panel">
      <h3>活动基础信息</h3>
      <p class="p-sub">日期与时间为原生 input 控件，请选择后提交排期。</p>

      <div class="grid-form">
        <div class="fld">
          <span class="f-label">活动名称</span>
          <input v-model="name" type="text" class="native" placeholder="请输入活动名称" />
        </div>
        <div class="fld">
          <span class="f-label">开始日期</span>
          <input v-model="startDate" type="date" class="native" />
        </div>
        <div class="fld">
          <span class="f-label">结束日期</span>
          <input v-model="endDate" type="date" class="native" />
        </div>
        <div class="fld">
          <span class="f-label">开始时间</span>
          <input v-model="startTime" type="time" class="native" />
        </div>
        <div class="fld">
          <span class="f-label">开售时刻</span>
          <input v-model="saleAt" type="datetime-local" class="native" />
        </div>
      </div>

      <div class="toolbar">
        <el-button type="primary" @click="submit">提交排期</el-button>
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
import { ElMessage } from 'element-plus'

const name = ref('')
const startDate = ref('')
const endDate = ref('')
const startTime = ref('')
const saleAt = ref('')
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function submit() {
  const text = {
    name: name.value.trim(),
    startDate: startDate.value,
    endDate: endDate.value,
    startTime: startTime.value,
    saleAt: saleAt.value
  }
  const empties = Object.entries(text).filter(([, v]) => !v).map(([k]) => k)
  if (empties.length) {
    ElMessage.warning('请完整填写排期信息')
    return
  }
  logs.value.unshift({
    time: stamp(),
    text: `排期已提交：「${text.name}」 ${text.startDate} ~ ${text.endDate} ${text.startTime}，开售 ${text.saleAt}`
  })
}
</script>

<style scoped>
.grid-form {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  max-width: 780px;
}
.fld { display: flex; flex-direction: column; gap: 6px; }
.f-label { font-size: 12px; color: var(--text-3); }
.native {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 10px;
  border: 1px solid #c4bfae;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  font-family: inherit;
}
.native:focus { border-color: var(--brand); }
</style>
