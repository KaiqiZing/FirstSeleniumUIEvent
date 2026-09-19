<template>
  <div class="page">
    <div class="page-title">客户工单录入</div>
    <p class="page-desc">页面包含受控表单输入、异步联想搜索与输入清空等环节。</p>

    <section class="panel">
      <h3>工单基础信息</h3>
      <p class="p-sub">提交时以框架内部状态为准，若未正确触发输入事件则视为未录入。</p>
      <div class="row-form">
        <div class="fld">
          <span class="f-label">客户名称</span>
          <el-input v-model="custName" placeholder="请输入客户名称" style="width: 260px" />
        </div>
        <div class="fld">
          <span class="f-label">工单类型</span>
          <el-select v-model="ticketType" placeholder="请选择工单类型" style="width: 220px">
            <el-option label="故障报修" value="fix" />
            <el-option label="咨询建议" value="advice" />
            <el-option label="投诉处理" value="complaint" />
          </el-select>
        </div>
        <el-button type="primary" @click="submitTicket">校验并提交</el-button>
      </div>
    </section>

    <section class="panel">
      <h3>搜索联想</h3>
      <p class="p-sub">逐字输入关键词，停顿后会展示联想结果；中文联想依赖输入事件触发。</p>
      <div class="search-wrap">
        <el-input v-model="keyword" placeholder="输入关键词，如：发票" clearable style="width: 320px" @input="onKeyword" />
        <div v-if="suggestions.length" class="suggest">
          <div
            v-for="s in suggestions"
            :key="s"
            class="suggest-item"
            @click="pickSuggestion(s)"
          >
            {{ s }}
          </div>
        </div>
      </div>
      <div class="toolbar">
        <el-button size="small" @click="searchSubmit">搜索</el-button>
        <span class="muted" style="font-size: 12px">最近选中：{{ keyword || '—' }}</span>
      </div>
    </section>

    <section class="panel">
      <h3>备注与提交</h3>
      <p class="p-sub">先清空既有内容再录入新备注。</p>
      <div class="row-form">
        <div class="fld" style="flex: 1">
          <span class="f-label">处理备注</span>
          <el-input v-model="remark" type="textarea" :rows="3" placeholder="请输入处理备注" />
        </div>
      </div>
      <div class="toolbar">
        <el-button @click="clearRemark">清空备注</el-button>
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

const custName = ref('')
const ticketType = ref('')
const keyword = ref('')
const remark = ref('')
const suggestions = ref([])
const logs = ref([])
let timer = null
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

const POOL = ['发票冲红', '发票抬头变更', '电子发票下载', '发票丢失补办', '合同模板下载', '返利结算说明', '退换货流程', '对账单导出']

function submitTicket() {
  const name = custName.value.trim()
  if (!name || !ticketType.value) {
    ElMessage.warning('客户名称或工单类型未录入（请通过真实键入方式填写）')
    logs.value.unshift({ time: stamp(), text: `校验未通过：状态内客户名称「${custName.value}」，工单类型「${ticketType.value || '未选择'}」` })
    return
  }
  logs.value.unshift({ time: stamp(), text: `工单已提交：客户「${name}」，类型「${ticketType.value}」` })
}

function onKeyword() {
  clearTimeout(timer)
  suggestions.value = []
  const kw = keyword.value.trim()
  if (!kw) return
  timer = setTimeout(() => {
    suggestions.value = POOL.filter((p) => p.includes(kw)).slice(0, 6)
  }, 700)
}

function pickSuggestion(s) {
  keyword.value = s
  suggestions.value = []
}

function searchSubmit() {
  if (!keyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  logs.value.unshift({ time: stamp(), text: `执行搜索：关键词「${keyword.value}」` })
}

function clearRemark() {
  remark.value = ''
  logs.value.unshift({ time: stamp(), text: '备注已清空，可重新录入' })
}
</script>

<style scoped>
.search-wrap { position: relative; display: inline-block; }
.suggest {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 320px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: 0 10px 24px rgba(31, 35, 41, 0.12);
  z-index: 20;
  padding: 5px;
}
.suggest-item {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  color: var(--text-1);
}
.suggest-item:hover { background: var(--brand-soft); color: var(--brand-2); }
</style>
