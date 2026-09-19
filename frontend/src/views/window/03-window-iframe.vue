<template>
  <div class="page">
    <div class="page-title">采购申请处理</div>
    <p class="page-desc">采购申请表单在新窗口内打开，表单中又嵌入了报销业务框架。</p>

    <section class="panel">
      <h3>采购申请单</h3>
      <p class="p-sub">请先在新窗口内完成内层表单的填写与提交，再回到本窗口登记主档。</p>

      <el-table :data="applies" size="small" border style="width: 100%">
        <el-table-column prop="no" label="申请单号" width="190" />
        <el-table-column prop="subject" label="采购事项" min-width="200" />
        <el-table-column prop="amount" label="预算金额（元）" width="150" />
        <el-table-column prop="owner" label="申请人" width="120" />
      </el-table>

      <div class="toolbar" style="margin-top: 12px">
        <el-button type="primary" @click="openInWindow">在新窗口处理申请</el-button>
        <el-button @click="registerMain">登记主档处理结论</el-button>
        <span class="muted" style="font-size: 12px">已登记主档：{{ mainCount }} 次</span>
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

const applies = [
  { no: 'PR-2026-091', subject: '办公区工位家具采购', amount: '42,000.00', owner: '行政部 周敏' },
  { no: 'PR-2026-092', subject: '季度营销物料制作', amount: '18,600.00', owner: '市场部 陈立' }
]
const mainCount = ref(0)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function openInWindow() {
  const w = window.open('/iframes/frame-a.html', 'procWindow', 'width=1080,height=760')
  logs.value.unshift({
    time: stamp(),
    text: w
      ? '已在新窗口打开申请处理页（内含一层 iframe，iframe 内又有二层表单）'
      : '新窗口打开失败（返回 null，可能被浏览器拦截）'
  })
  if (!w) ElMessage.warning('新窗口未能打开')
}

function registerMain() {
  mainCount.value += 1
  logs.value.unshift({ time: stamp(), text: `主档登记完成：第 ${mainCount.value} 次（需先切换回主窗口句柄操作）` })
}
</script>
