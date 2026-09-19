<template>
  <div class="page">
    <div class="page-title">销售单据列表</div>
    <p class="page-desc">点击单据名称会在新标签页中打开详情，原列表页面保持不变。</p>

    <section class="panel">
      <h3>本月销售单据</h3>
      <p class="p-sub">单据详情通过 target=_blank 在新标签页打开。</p>
      <el-table :data="orders" size="small" border style="width: 100%">
        <el-table-column label="单据号" width="190">
          <template #default="{ row }">
            <a class="bill-link" :href="`/iframes/detail.html?id=${row.no}`" target="_blank">{{ row.no }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="cust" label="客户" min-width="180" />
        <el-table-column prop="amount" label="金额（元）" width="150" />
        <el-table-column prop="state" label="状态" width="110" />
        <el-table-column prop="date" label="开单日期" width="120" />
      </el-table>
      <div class="toolbar" style="margin-top: 12px">
        <el-button @click="openFake">通过脚本打开一个空白新标签</el-button>
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

const orders = [
  { no: 'SO-20260901-118', cust: '华东-直营店', amount: '2,680.00', state: '待确认', date: '2026-09-01' },
  { no: 'SO-20260902-045', cust: '华南-加盟店', amount: '18,200.50', state: '已发货', date: '2026-09-02' },
  { no: 'SO-20260903-091', cust: '华北-经销商', amount: '96,000.00', state: '已完成', date: '2026-09-03' },
  { no: 'SO-20260904-132', cust: '西南-分销商', amount: '5,430.75', state: '待确认', date: '2026-09-04' }
]
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function openFake() {
  const w = window.open('', '_blank')
  if (w) w.document.title = '新标签占位页'
  logs.value.unshift({
    time: stamp(),
    text: '已通过脚本触发打开新标签' + (w ? '（成功）' : '（返回空，可能被拦截）')
  })
}
</script>

<style scoped>
.bill-link {
  color: var(--brand-2);
  font-family: Consolas, Menlo, monospace;
  font-size: 13px;
}
.bill-link:hover { text-decoration: underline; }
</style>
