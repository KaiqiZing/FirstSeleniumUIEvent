<template>
  <div class="page">
    <div class="page-title">交接记录登记</div>
    <p class="page-desc">记录一次系统交接操作，含基础资料与高级配置两个区块。</p>

    <section class="panel">
      <h3>基础交接信息</h3>
      <p class="p-sub">必填项带红色星标，保存前需确认交接须知。</p>
      <div class="row-form">
        <div class="fld">
          <span class="f-label"><i class="req">*</i>交接操作人</span>
          <el-input v-model="operator" placeholder="请输入交接操作人" style="width: 240px" />
        </div>
        <div class="fld">
          <span class="f-label"><i class="req">*</i>交接说明</span>
          <el-input v-model="note" type="textarea" :rows="2" placeholder="请输入交接说明" style="width: 420px" />
        </div>
      </div>
      <div class="toolbar" style="margin-top: 14px">
        <el-checkbox v-model="agreed">我已阅读并同意《数据变更与交接须知》</el-checkbox>
      </div>
      <div class="toolbar">
        <el-button type="primary" :disabled="!canSave" @click="doSave">保存交接记录</el-button>
        <el-button disabled>批量迁移（未获得该权限）</el-button>
        <span class="muted" style="font-size: 12px">批量迁移按钮当前不可用</span>
      </div>
    </section>

    <section class="panel">
      <h3>高级配置</h3>
      <p class="p-sub">折叠区块，展开后才会渲染内部配置项。</p>
      <el-collapse v-model="activeCollapse">
        <el-collapse-item name="adv" title="展开查看高级配置">
          <div class="row-form">
            <div class="fld">
              <span class="f-label">审核人</span>
              <el-input v-model="reviewer" placeholder="请输入审核人" style="width: 220px" />
            </div>
            <el-button type="primary" plain @click="doApplyAdv">应用高级配置</el-button>
          </div>
        </el-collapse-item>
      </el-collapse>
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

const operator = ref('')
const note = ref('')
const agreed = ref(false)
const reviewer = ref('')
const activeCollapse = ref([])
const logs = ref([])

const canSave = computed(() => agreed.value && operator.value.trim())
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function doSave() {
  logs.value.unshift({
    time: stamp(),
    text: `交接记录已保存：操作人「${operator.value.trim()}」，说明「${note.value.trim() || '（空）'}」`
  })
  ElMessage.success('保存成功')
}

function doApplyAdv() {
  logs.value.unshift({
    time: stamp(),
    text: `高级配置已应用：审核人「${reviewer.value.trim() || '（未设置）'}」`
  })
}
</script>

<style scoped>
.req { color: var(--danger); font-style: normal; margin-right: 2px; }
</style>
