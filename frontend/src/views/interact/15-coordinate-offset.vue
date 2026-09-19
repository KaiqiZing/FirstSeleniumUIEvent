<template>
  <div class="page">
    <div class="page-title">门店平面定位</div>
    <p class="page-desc">定位区域存在缩放与溢出裁切，目标点位可能位于裁切区域外。</p>

    <section class="panel">
      <div class="bar">
        <div>
          <h3>平面定位图</h3>
          <p class="p-sub">缩略图默认裁切，展开完整区域后才可点到裁切外的目标点位。</p>
        </div>
        <div class="bar-actions">
          <el-button size="small" @click="expanded = !expanded">
            {{ expanded ? '恢复缩略裁切' : '展开完整区域' }}
          </el-button>
        </div>
      </div>

      <div class="stage" :class="{ expanded }">
        <div class="floor">
          <div class="zone-tag t1">收银区</div>
          <div class="zone-tag t2">货架区</div>
          <div class="zone-tag t3">仓储区</div>
          <button type="button" ref="targetRef" class="target-dot" @click="markTarget">目标货架</button>
        </div>
      </div>

      <div class="toolbar">
        <el-button type="primary" @click="inspectCoord">获取目标点位坐标</el-button>
        <span class="muted" style="font-size: 12px">输出目标元素在视口中的几何信息</span>
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
import { ref, nextTick } from 'vue'

const expanded = ref(false)
const targetRef = ref(null)
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

function markTarget() {
  logs.value.unshift({ time: stamp(), text: '目标货架已标记，点位已写入定位单' })
}

async function inspectCoord() {
  await nextTick()
  const el = targetRef.value
  if (!el) {
    logs.value.unshift({ time: stamp(), text: '未找到目标点位元素' })
    return
  }
  const r = el.getBoundingClientRect()
  const cs = getComputedStyle(el)
  logs.value.unshift({
    time: stamp(),
    text: `目标点位 rect：x=${r.x.toFixed(0)} y=${r.y.toFixed(0)} w=${r.width.toFixed(0)} h=${r.height.toFixed(0)}，devicePixelRatio=${window.devicePixelRatio}，缩放上下文 transform=${cs.transform || 'none'}`
  })
}
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: flex-start; }
.bar h3 { margin: 0 0 4px; font-size: 15px; }
.bar p { margin: 0; }
.stage {
  margin-top: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}
.floor {
  position: relative;
  width: 900px;
  height: 420px;
  background:
    linear-gradient(rgba(47, 111, 92, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(47, 111, 92, 0.05) 1px, transparent 1px),
    var(--paper);
  background-size: 26px 26px;
}
.stage.expanded { overflow: visible; }
.zone-tag {
  position: absolute;
  font-size: 12px;
  color: var(--text-3);
  background: rgba(47, 111, 92, 0.08);
  border: 1px solid var(--brand-line);
  border-radius: 6px;
  padding: 4px 10px;
}
.t1 { top: 22px; left: 22px; }
.t2 { top: 22px; left: 320px; }
.t3 { top: 300px; left: 620px; }
.target-dot {
  position: absolute;
  left: 700px;
  bottom: -40px;
  border: 0;
  background: var(--brand);
  color: #fff;
  font-size: 13px;
  border-radius: 8px;
  padding: 9px 14px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(47, 111, 92, 0.4);
}
.stage:not(.expanded) .target-dot { pointer-events: auto; }
</style>
