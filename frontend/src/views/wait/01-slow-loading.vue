<template>
  <div class="page">
    <div class="page-title">对账数据查询</div>
    <p class="page-desc">服务端响应耗时随环境档位不同，查询期间页面出现加载遮罩。</p>

    <section class="panel">
      <div class="row-form">
        <div class="fld">
          <span class="f-label">环境档位</span>
          <el-radio-group v-model="envDelay">
            <el-radio-button :value="0.5">较快（0.5s）</el-radio-button>
            <el-radio-button :value="3">常规（3s）</el-radio-button>
            <el-radio-button :value="8">较慢（8s）</el-radio-button>
          </el-radio-group>
        </div>
        <el-button type="primary" @click="query">查询对账数据</el-button>
      </div>

      <div v-loading="busy" element-loading-text="数据加载中，请稍候…" class="table-wrap">
        <template v-if="rows.length">
          <el-table :data="rows" size="small" border style="width: 100%">
            <el-table-column prop="id" label="数据编号" width="110" />
            <el-table-column prop="name" label="对账对象" min-width="180" />
            <el-table-column prop="owner" label="负责人" width="120" />
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column prop="updated" label="更新时间" width="110" />
          </el-table>
        </template>
        <div v-else-if="!busy" class="empty-hint" style="text-align: center; padding: 30px">
          尚无数据，请先执行查询
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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../utils/http'

const envDelay = ref(3)
const busy = ref(false)
const rows = ref([])
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

async function query() {
  if (busy.value) return
  busy.value = true
  rows.value = []
  const start = Date.now()
  const hint = { time: stamp(), text: `发起查询请求（环境档位 ${envDelay.value}s）…` }
  logs.value.unshift(hint)
  try {
    const data = await http.get('/slow/items', { params: { delay: envDelay.value }, timeout: 20000 })
    rows.value = data.rows
    logs.value.unshift({
      time: stamp(),
      text: `查询完成：返回 ${data.rows.length} 条，实际耗时 ${((Date.now() - start) / 1000).toFixed(2)}s`
    })
    ElMessage.success('查询完成')
  } catch (err) {
    console.error(err)
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.table-wrap {
  margin-top: 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  min-height: 120px;
}
</style>
