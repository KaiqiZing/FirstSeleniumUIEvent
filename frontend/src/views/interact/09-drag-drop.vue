<template>
  <div class="page">
    <div class="page-title">配送任务分配</div>
    <p class="page-desc">将候选配送员拖入右侧已选区完成分配，支持拖回重新分配。</p>

    <section class="panel">
      <h3>任务分配面板</h3>
      <p class="p-sub">拖拽源与放置区均基于原生拖放事件（dragstart / drop）。</p>

      <div class="dnd-wrap">
        <div class="zone">
          <div class="zone-head">候选配送员</div>
          <div
            class="zone-body"
            :class="{ over: over === 'cand' }"
            @dragover.prevent="over = 'cand'"
            @dragleave="over = ''"
            @drop.prevent="onDrop($event, 'cand')"
          >
            <div
              v-for="c in candidates"
              :key="c.id"
              class="chip"
              draggable="true"
              @dragstart="onDrag($event, c)"
            >
              <span class="chip-name">{{ c.name }}</span>
              <span class="chip-zone">{{ c.zone }}</span>
            </div>
            <div v-if="!candidates.length" class="zone-empty">无候选，可将已选拖回</div>
          </div>
        </div>

        <div class="zone">
          <div class="zone-head">已选配送员（{{ picked.length }}）</div>
          <div
            class="zone-body"
            :class="{ over: over === 'picked' }"
            @dragover.prevent="over = 'picked'"
            @dragleave="over = ''"
            @drop.prevent="onDrop($event, 'picked')"
          >
            <div
              v-for="c in picked"
              :key="c.id"
              class="chip picked"
              draggable="true"
              @dragstart="onDrag($event, c)"
            >
              <span class="chip-name">{{ c.name }}</span>
              <span class="chip-zone">{{ c.zone }}</span>
            </div>
            <div v-if="!picked.length" class="zone-empty">将候选拖放到这里</div>
          </div>
        </div>
      </div>

      <div class="toolbar">
        <el-button type="primary" @click="commit">确认分配</el-button>
        <el-button @click="reset">重置分配</el-button>
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

const POOL = [
  { id: 'D-01', name: '陈师傅', zone: '城东片区' },
  { id: 'D-02', name: '林师傅', zone: '城西片区' },
  { id: 'D-03', name: '周师傅', zone: '城南片区' },
  { id: 'D-04', name: '吴师傅', zone: '城北片区' },
  { id: 'D-05', name: '郑师傅', zone: '高新区' }
]

const candidates = ref([...POOL])
const picked = ref([])
const over = ref('')
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function onDrag(ev, item) {
  ev.dataTransfer.setData('text/plain', item.id)
  ev.dataTransfer.effectAllowed = 'move'
}

function onDrop(ev, target) {
  over.value = ''
  const id = ev.dataTransfer.getData('text/plain')
  if (!id) return
  const from = candidates.value.find((x) => x.id === id) ? 'candidates' : 'picked'
  const item = from === 'candidates' ? candidates.value.find((x) => x.id === id) : picked.value.find((x) => x.id === id)
  if (!item) return
  if (from === 'candidates') {
    candidates.value = candidates.value.filter((x) => x.id !== id)
    picked.value = [...picked.value, item]
  } else if (target === 'cand') {
    picked.value = picked.value.filter((x) => x.id !== id)
    candidates.value = [...candidates.value, item]
  }
  logs.value.unshift({ time: stamp(), text: `已拖放 ${item.name} 至「${target === 'picked' ? '已选区' : '候选区'}」` })
}

function commit() {
  if (!picked.value.length) {
    ElMessage.warning('请先拖拽至少一位配送员到已选区')
    return
  }
  logs.value.unshift({
    time: stamp(),
    text: `分配确认：已选 ${picked.value.length} 人（${picked.value.map((x) => x.name).join('、')}）`
  })
}

function reset() {
  candidates.value = [...POOL]
  picked.value = []
  logs.value.unshift({ time: stamp(), text: '已重置分配面板' })
}
</script>

<style scoped>
.dnd-wrap { display: flex; gap: 16px; align-items: stretch; }
.zone { flex: 1; min-width: 0; }
.zone-head {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-2);
}
.zone-body {
  min-height: 190px;
  border: 1.5px dashed #c4bfae;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--paper);
  transition: all 0.15s ease;
}
.zone-body.over { border-color: var(--brand); background: var(--brand-soft); }
.chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  cursor: grab;
  user-select: none;
}
.chip:active { cursor: grabbing; }
.chip.picked { border-color: var(--brand-line); background: var(--brand-soft); }
.chip-name { font-size: 13px; font-weight: 500; }
.chip-zone { font-size: 12px; color: var(--text-3); }
.zone-empty {
  color: #c4bfae;
  font-size: 13px;
  text-align: center;
  margin: auto;
}
</style>
