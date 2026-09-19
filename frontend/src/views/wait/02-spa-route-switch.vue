<template>
  <div class="page">
    <div class="page-title">经营看板</div>
    <p class="page-desc">
      看板在单页内部切换子视图，切换时地址栏变化但不触发整页刷新。
      本页打开时刻：{{ pageBorn }}，页面已存活 {{ alive }}s。
    </p>

    <section class="panel">
      <h3>看板子视图</h3>
      <p class="p-sub">通过下方入口切换「经营概览 / 收支明细 / 绩效对比」三个子视图。</p>

      <div class="tab-row">
        <button type="button" class="tab-btn" :class="{ active: view === 'overview' }" @click="switchTo('overview')">
          经营概览
        </button>
        <button type="button" class="tab-btn" :class="{ active: view === 'flow' }" @click="switchTo('flow')">
          收支明细
        </button>
        <button type="button" class="tab-btn" :class="{ active: view === 'kpi' }" @click="switchTo('kpi')">
          绩效对比
        </button>
      </div>

      <div v-if="view === 'overview'" class="view-card">
        <strong>经营概览</strong>
        <p>本月累计成交 1,286 单，营收 ¥ 4,820,116.00，回款率 87.6%。</p>
        <div class="metrics">
          <span>成交订单 <b>1,286</b></span>
          <span>新增客户 <b>214</b></span>
          <span>售后率 <b>1.9%</b></span>
        </div>
      </div>
      <div v-else-if="view === 'flow'" class="view-card">
        <strong>收支明细</strong>
        <p>收入主要来自经销订货与渠道返利，支出集中在大促补贴与物流费用。</p>
        <div class="metrics">
          <span>本月收入 <b>¥ 4,820,116</b></span>
          <span>本月支出 <b>¥ 1,906,320</b></span>
        </div>
      </div>
      <div v-else class="view-card">
        <strong>绩效对比</strong>
        <p>对比各区域人均产出与客单价，华东区连续三月领先。</p>
        <div class="metrics">
          <span>人均产出 <b>¥ 68,400</b></span>
          <span>平均客单 <b>¥ 3,748</b></span>
        </div>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const view = computed(() => (route.query.view === 'flow' || route.query.view === 'kpi' ? route.query.view : 'overview'))
const pageBorn = ref('')
const alive = ref(0)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })
let timer = null

function switchTo(name) {
  router.replace({ query: { view: name } })
  logs.value.unshift({ time: stamp(), text: `子视图切换为「${name}」（URL：${route.path}?view=${name}，页面未整页刷新）` })
}

watch(view, () => logs.value.unshift({ time: stamp(), text: `当前子视图：${view.value}` }))

onMounted(() => {
  pageBorn.value = stamp()
  alive.value = 0
  timer = setInterval(() => alive.value++, 1000)
  logs.value.unshift({ time: pageBorn.value, text: `看板页面完成初始化，子视图：${view.value}` })
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.tab-row { display: flex; gap: 10px; margin-bottom: 14px; }
.tab-btn {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 7px;
  padding: 7px 16px;
  font-size: 13px;
  cursor: pointer;
  color: var(--text-2);
  transition: all 0.15s;
}
.tab-btn.active { border-color: var(--brand); background: var(--brand-soft); color: var(--brand-2); font-weight: 500; }
.tab-btn:hover { border-color: var(--brand-3); }
.view-card { border: 1px solid var(--line-soft); border-radius: 8px; padding: 16px; background: var(--paper); }
.view-card strong { font-size: 15px; }
.view-card p { color: var(--text-2); line-height: 1.8; font-size: 13px; margin: 8px 0 12px; }
.metrics { display: flex; gap: 26px; }
.metrics span { font-size: 12px; color: var(--text-3); }
.metrics b { display: block; font-size: 18px; color: var(--brand-2); margin-top: 2px; }
</style>
