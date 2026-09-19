<template>
  <div class="page">
    <div class="page-title">公告编辑器</div>
    <p class="page-desc">在富文本编辑区撰写运营公告正文，支持基础排版后提交发布。</p>

    <section class="panel">
      <h3>撰写公告</h3>
      <p class="p-sub">标题输入后，在正文区域进行排版并提交。</p>

      <div class="row-form">
        <div class="fld" style="flex: 1">
          <span class="f-label">公告标题</span>
          <el-input v-model="title" placeholder="请输入公告标题" />
        </div>
      </div>

      <div style="margin-top: 14px">
        <div class="ed-toolbar">
          <button type="button" title="加粗" @click="exec('bold')"><b>B</b></button>
          <button type="button" title="斜体" @click="exec('italic')"><i>I</i></button>
          <button type="button" title="下划线" @click="exec('underline')"><u>U</u></button>
          <span class="divider"></span>
          <button type="button" title="插入无序列表" @click="exec('insertUnorderedList')">列表</button>
          <button type="button" title="清除格式" @click="exec('removeFormat')">清除格式</button>
        </div>
        <div
          ref="editorRef"
          class="ed-area"
          contenteditable="true"
          data-placeholder="请输入公告正文，支持加粗、斜体、列表等排版…"
          @input="onInput"
        ></div>
      </div>

      <div class="toolbar">
        <el-button type="primary" @click="publish">发布公告</el-button>
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

const title = ref('')
const editorRef = ref(null)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function exec(cmd) {
  editorRef.value?.focus()
  document.execCommand(cmd, false, null)
  onInput()
}

function onInput() {
  const el = editorRef.value
  if (!el) return
  if (el.textContent.trim()) el.classList.remove('empty')
  else el.classList.add('empty')
}

function publish() {
  const text = (editorRef.value?.textContent || '').trim()
  if (!title.value.trim() || !text) {
    ElMessage.warning('请填写公告标题与正文内容')
    return
  }
  logs.value.unshift({
    time: stamp(),
    text: `公告已发布：「${title.value.trim()}」，正文字数 ${text.length}`
  })
}
</script>

<style scoped>
.ed-toolbar {
  display: flex;
  gap: 6px;
  align-items: center;
  border: 1px solid #c4bfae;
  border-bottom: 0;
  border-radius: 8px 8px 0 0;
  background: var(--paper);
  padding: 8px 10px;
}
.ed-toolbar button {
  border: 1px solid transparent;
  background: transparent;
  border-radius: 5px;
  min-width: 32px;
  height: 28px;
  cursor: pointer;
  color: var(--text-2);
  font-size: 13px;
}
.ed-toolbar button:hover { background: var(--brand-soft); color: var(--brand-2); }
.divider { width: 1px; height: 18px; background: var(--line); margin: 0 4px; }
.ed-area {
  border: 1px solid #c4bfae;
  border-radius: 0 0 8px 8px;
  min-height: 170px;
  padding: 12px 14px;
  outline: none;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-1);
  background: #fff;
}
.ed-area.empty::before {
  content: attr(data-placeholder);
  color: #c4bfae;
  pointer-events: none;
}
</style>
