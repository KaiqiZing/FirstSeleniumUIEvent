<template>
  <div class="page">
    <div class="page-title">对账批次管理</div>
    <p class="page-desc">生成对账结果期间页面出现全屏计算遮罩，遮罩消失后才可下载结果。</p>

    <section class="panel">
      <h3>对账批次</h3>
      <p class="p-sub">最近一批对账数据，处理中会锁定页面操作。</p>

      <div class="stage" :class="{ busy: busy }">
        <el-table :data="rows" size="small" style="width: 100%">
          <el-table-column prop="batch" label="批次号" width="180" />
          <el-table-column prop="scope" label="对账范围" />
          <el-table-column prop="amount" label="金额（元）" width="140" />
          <el-table-column prop="updated" label="更新时间" width="120" />
        </el-table>

        <div v-if="busy" class="mask">
          <div class="mask-inner">
            <el-icon class="is-loading" :size="26"><Loading /></el-icon>
            <span>对账计算中，请稍候…</span>
          </div>
        </div>
      </div>

      <div class="toolbar">
        <el-button type="primary" @click="generate">生成对账结果</el-button>
        <el-button :type="ready ? 'success' : 'default'" plain :disabled="!ready" @click="download">
          <el-icon style="margin-right: 4px"><Download /></el-icon>
          下载对账结果
        </el-button>
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
import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Download } from '@element-plus/icons-vue'

const rows = [
  { batch: 'R-2609-01', scope: '2026-08 全量流水', amount: '1,284,930.55', updated: '09-02 18:20' },
  { batch: 'R-2609-02', scope: '渠道返利专项', amount: '86,120.00', updated: '09-05 10:05' },
  { batch: 'R-2609-03', scope: '手续费核对', amount: '9,402.18', updated: '09-06 09:41' }
]
const busy = ref(false)
const ready = ref(false)
const logs = ref([])
let timer = null

const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function generate() {
  if (busy.value) return
  busy.value = true
  ready.value = false
  logs.value.unshift({ time: stamp(), text: '已发起对账生成请求，开始计算…' })
  timer = setTimeout(() => {
    busy.value = false
    ready.value = true
    logs.value.unshift({ time: stamp(), text: '对账计算完成，可以下载结果文件' })
    ElMessage.success('对账完成')
  }, 3600)
}

function download() {
  logs.value.unshift({ time: stamp(), text: '已开始下载对账结果文件 result-2609.csv' })
  ElMessage.success('开始下载')
}

onUnmounted(() => clearTimeout(timer))
</script>

<style scoped>
.stage {
  position: relative;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}
.mask {
  position: absolute;
  inset: 0;
  z-index: 5;
  background: rgba(255, 255, 255, 0.78);
  display: flex;
  align-items: center;
  justify-content: center;
}
.mask-inner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 22px;
  box-shadow: 0 8px 24px rgba(31, 35, 41, 0.12);
  color: var(--text-2);
  font-size: 13px;
}
</style>
