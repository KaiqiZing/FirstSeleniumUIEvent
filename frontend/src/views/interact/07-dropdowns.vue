<template>
  <div class="page">
    <div class="page-title">销售报表筛选</div>
    <p class="page-desc">筛选区同时提供原生下拉（区域）与业务组件下拉（业务类型）两类控件。</p>

    <section class="panel">
      <h3>原生下拉：区域</h3>
      <p class="p-sub">使用浏览器原生 select 渲染，选项位于表单内部。</p>
      <div class="row-form">
        <div class="fld">
          <span class="f-label">选择区域</span>
          <select v-model="region" class="native-select">
            <option value="">请选择区域</option>
            <option value="east">华东大区</option>
            <option value="north">华北直辖区</option>
            <option value="south">华南大区</option>
            <option value="west">西南大区</option>
          </select>
        </div>
        <div class="fld">
          <span class="f-label">账期</span>
          <select v-model="period" class="native-select">
            <option value="2026-08">2026 年 8 月</option>
            <option value="2026-07">2026 年 7 月</option>
            <option value="2026-06">2026 年 6 月</option>
          </select>
        </div>
        <el-button type="primary" @click="queryNative">按原生条件查询</el-button>
      </div>
    </section>

    <section class="panel">
      <h3>业务组件下拉：业务类型</h3>
      <p class="p-sub">组件下拉为自定义渲染，选项列表挂载在页面根节点（浮层）上。</p>
      <div class="row-form">
        <div class="fld">
          <span class="f-label">选择业务类型</span>
          <el-select v-model="bizType" placeholder="请选择业务类型" style="width: 220px">
            <el-option label="经销订货" value="order" />
            <el-option label="直营零售" value="retail" />
            <el-option label="渠道返利" value="rebate" />
            <el-option label="售后理赔" value="claim" />
            <el-option label="促销分摊" value="promo" />
          </el-select>
        </div>
        <div class="fld">
          <span class="f-label">门店范围</span>
          <el-select v-model="scope" placeholder="请选择门店范围" style="width: 220px">
            <el-option label="全部门店" value="all" />
            <el-option label="仅直营店" value="direct" />
            <el-option label="仅加盟店" value="franchise" />
          </el-select>
        </div>
        <el-button type="primary" @click="queryBiz">按业务组件条件查询</el-button>
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

const region = ref('')
const period = ref('')
const bizType = ref('')
const scope = ref('')
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

const REGION_TEXT = { east: '华东大区', north: '华北直辖区', south: '华南大区', west: '西南大区' }
const PERIOD_TEXT = { '2026-08': '2026 年 8 月', '2026-07': '2026 年 7 月', '2026-06': '2026 年 6 月' }

function queryNative() {
  if (!region.value || !period.value) {
    ElMessage.warning('请选择区域与账期')
    return
  }
  logs.value.unshift({
    time: stamp(),
    text: `原生条件查询：区域「${REGION_TEXT[region.value]}」账期「${PERIOD_TEXT[period.value]}」`
  })
}

function queryBiz() {
  if (!bizType.value || !scope.value) {
    ElMessage.warning('请选择业务类型与门店范围')
    return
  }
  logs.value.unshift({
    time: stamp(),
    text: `组件条件查询：业务类型「${bizType.value}」门店范围「${scope.value}」`
  })
}
</script>

<style scoped>
.native-select {
  width: 220px;
  box-sizing: border-box;
  padding: 8px 10px;
  border: 1px solid #c4bfae;
  border-radius: 6px;
  background: #fff;
  font-size: 13px;
  outline: none;
  appearance: auto;
}
</style>
