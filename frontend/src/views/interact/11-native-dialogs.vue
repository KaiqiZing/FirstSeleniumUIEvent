<template>
  <div class="page">
    <div class="page-title">库存预警处理</div>
    <p class="page-desc">页面使用浏览器原生弹窗完成告警确认、复核确认与备注录入。</p>

    <section class="panel">
      <h3>低库存告警</h3>
      <p class="p-sub">下面商品触发告警，逐个点击操作按钮处理弹窗。</p>
      <el-table :data="rows" size="small" border style="width: 100%">
        <el-table-column prop="sku" label="SKU" width="170" />
        <el-table-column prop="name" label="商品名称" min-width="200" />
        <el-table-column prop="stock" label="当前库存" width="110" />
        <el-table-column prop="threshold" label="预警阈值" width="110" />
        <el-table-column label="操作" width="230">
          <template #default="{ row }">
            <el-button link type="primary" @click="showAlert(row)">查看告警</el-button>
            <el-button link type="warning" @click="confirmReplenish(row)">确认补货</el-button>
            <el-button link @click="promptNote(row)">登记备注</el-button>
          </template>
        </el-table-column>
      </el-table>
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

const rows = [
  { sku: 'SKU-23891', name: '无线降噪耳机 Pro', stock: 6, threshold: 10 },
  { sku: 'SKU-23892', name: '智能手表 S2', stock: 3, threshold: 8 },
  { sku: 'SKU-23893', name: '快充充电宝 10000mAh', stock: 12, threshold: 15 }
]
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function showAlert(row) {
  window.alert(`商品 ${row.name}（${row.sku}）当前库存 ${row.stock}，低于预警阈值 ${row.threshold}，请及时处理。`)
  logs.value.unshift({ time: stamp(), text: `已查看告警：${row.name}` })
}

function confirmReplenish(row) {
  const ok = window.confirm(`确认对「${row.name}」发起补货申请吗？\n预计补货数量：${row.threshold * 3} 件`)
  logs.value.unshift({
    time: stamp(),
    text: `补货确认弹窗：用户选择「${ok ? '确定' : '取消'}」`
  })
}

function promptNote(row) {
  const note = window.prompt(`请登记针对「${row.name}」的处理备注：`, '')
  if (note === null) {
    logs.value.unshift({ time: stamp(), text: '备注录入弹窗：用户取消了录入' })
  } else {
    logs.value.unshift({ time: stamp(), text: `已登记备注：${note}` })
  }
}
</script>
