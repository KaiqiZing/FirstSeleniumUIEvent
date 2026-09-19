<template>
  <div class="page">
    <div class="page-title">资产信息登记</div>
    <p class="page-desc">本页控件的 id 与 class 由前端按渲染批次生成，每次生成都会变化；placeholder 与按钮文字保持不变。</p>

    <section class="panel">
      <h3>资产登记表单</h3>
      <p class="p-sub">以下属性为当前渲染批次生成：</p>
      <div class="attr-line mono">
        field id = <b>{{ attrs.fieldId }}</b> · class = <b>{{ attrs.fieldCls }}</b>
        <br />
        submit id = <b>{{ attrs.btnId }}</b> · class = <b>{{ attrs.btnCls }}</b>
      </div>

      <div class="row-form" style="margin-top: 14px">
        <div class="fld">
          <span class="f-label">资产编号</span>
          <input
            :id="attrs.fieldId"
            :class="['gen-input', attrs.fieldCls]"
            v-model="assetNo"
            type="text"
            placeholder="请输入资产编号"
          />
        </div>
        <div class="fld">
          <span class="f-label">资产名称</span>
          <input
            :id="attrs.nameId"
            v-model="assetName"
            type="text"
            placeholder="请输入资产名称"
          />
        </div>
      </div>

      <div class="toolbar">
        <button :id="attrs.btnId" :class="['gen-btn', attrs.btnCls]" type="button" @click="submit">提交资产信息</button>
        <el-button @click="regenerate">重新生成控件属性</el-button>
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

const rand = () => Math.random().toString(36).slice(2, 8)
const attrs = ref(gen())
const assetNo = ref('')
const assetName = ref('')
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function gen() {
  return {
    fieldId: 'field_' + rand(),
    fieldCls: 'fc-' + rand(),
    nameId: 'name_' + rand(),
    btnId: 'btn_' + rand(),
    btnCls: 'bc-' + rand()
  }
}

function regenerate() {
  attrs.value = gen()
  logs.value.unshift({ time: stamp(), text: `已重新生成控件属性批次（id/class 全部变更）` })
}

function submit() {
  logs.value.unshift({
    time: stamp(),
    text: `资产信息已提交：编号「${assetNo.value.trim() || '（空）'}」名称「${assetName.value.trim() || '（空）'}」`
  })
  ElMessage.success('提交成功')
}
</script>

<style scoped>
.attr-line {
  font-size: 12px;
  color: var(--text-2);
  background: var(--brand-soft);
  border: 1px solid var(--brand-line);
  border-radius: 8px;
  padding: 10px 14px;
  line-height: 1.9;
}
.attr-line b { color: var(--brand-2); }
.gen-input,
input[type='text'] {
  box-sizing: border-box;
  width: 220px;
  padding: 8px 11px;
  border: 1px solid #c4bfae;
  border-radius: 6px;
  outline: none;
  font-size: 13px;
  transition: border-color 0.15s;
}
.gen-input:focus,
input[type='text']:focus {
  border-color: var(--brand);
  box-shadow: 0 0 0 2px rgba(47, 111, 92, 0.15);
}
.gen-btn {
  border: 1px solid var(--brand);
  background: var(--brand);
  color: #fff;
  border-radius: 6px;
  padding: 9px 18px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
}
.gen-btn:hover { background: var(--brand-2); }
</style>
