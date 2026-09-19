<template>
  <div class="page">
    <div class="page-title">合同资料上传</div>
    <p class="page-desc">选择本地合同文件后回显信息，确认后提交到服务端登记。</p>

    <section class="panel">
      <h3>合同登记</h3>
      <p class="p-sub">请选择一份本地文件（.pdf / .docx / .png 均可）。</p>

      <div class="upload-row">
        <input
          ref="fileRef"
          id="contractFile"
          type="file"
          accept=".pdf,.docx,.png,.jpg,.txt"
          class="file-input"
          @change="onFileChange"
        />
        <label for="contractFile" class="file-btn">选择合同文件</label>
        <span v-if="!selected" class="muted" style="font-size: 13px">未选择文件</span>
        <span v-else class="file-name">{{ selected.name }}（{{ sizeText(selected.size) }}）</span>
      </div>

      <div class="toolbar">
        <el-button type="primary" :disabled="!selected" @click="upload">提交登记</el-button>
        <el-button :disabled="!selected" @click="clearFile">重新选择</el-button>
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

const fileRef = ref(null)
const selected = ref(null)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function sizeText(size) {
  if (size < 1024) return size + ' B'
  return (size / 1024).toFixed(1) + ' KB'
}

function onFileChange(ev) {
  const file = ev.target.files && ev.target.files[0]
  selected.value = file || null
  if (file) {
    logs.value.unshift({ time: stamp(), text: `已选择本地文件：${file.name}（${sizeText(file.size)}）` })
  }
}

function clearFile() {
  selected.value = null
  if (fileRef.value) fileRef.value.value = ''
  logs.value.unshift({ time: stamp(), text: '已清空文件选择' })
}

async function upload() {
  if (!selected.value) return
  const fd = new FormData()
  fd.append('file', selected.value)
  try {
    const data = await http.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 20000 })
    logs.value.unshift({
      time: stamp(),
      text: `服务端已登记合同文件：${data.filename}（${sizeText(data.size)}），登记号 ${data.regNo}`
    })
    ElMessage.success('提交成功')
  } catch (err) {
    console.error(err)
  }
}
</script>

<style scoped>
.upload-row { display: flex; align-items: center; gap: 12px; }
.file-input { display: none; }
.file-btn {
  display: inline-block;
  border: 1px solid var(--brand);
  background: #fff;
  color: var(--brand);
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.file-btn:hover { background: var(--brand-soft); }
.file-name { font-size: 13px; color: var(--brand-2); }
</style>
