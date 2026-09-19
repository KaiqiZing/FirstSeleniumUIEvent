<template>
  <div class="home">
    <section class="hero">
      <div class="hero-left">
        <span class="nb-kicker">SELENIUM · UI SCENARIOS</span>
        <h1>UI 自动化问题<br />场景演练台</h1>
        <p class="sub-en">Reproduce the高频自动化疑难 as real business pages</p>
        <p class="hero-cn">将高频自动化疑难还原为真实业务页面，逐项进入并尝试完成页面交互。</p>
        <div class="chips">
          <span class="nb-chip">页面交互</span>
          <span class="nb-chip">等待响应</span>
          <span class="nb-chip">多窗口</span>
          <span class="nb-chip">兼容差异</span>
          <span class="nb-chip">加密核对</span>
        </div>
      </div>
      <div class="hero-stat">
        <div><b>{{ scenarios.length }}</b><span>个场景</span></div>
        <div><b>{{ groups.length }}</b><span>个分类</span></div>
      </div>
    </section>

    <section class="cards">
      <div v-for="g in groups" :key="g.key" class="stat-card" :style="{ '--tab': g.color }" @click="goAnchor(g.key)">
        <div class="sc-icon"><el-icon :size="20"><component :is="iconMap[g.key]" /></el-icon></div>
        <div class="sc-meta">
          <strong>{{ g.name }}</strong>
          <span>{{ g.desc }}</span>
        </div>
        <div class="sc-count">{{ countOf(g.key) }} 场景</div>
      </div>
    </section>

    <section v-for="g in groups" :id="g.key" :key="g.key" class="group">
      <div class="group-head">
        <i class="tab-piece" :style="{ '--tab': g.color }"></i>
        <div class="group-name">{{ g.name }}</div>
        <span class="group-count">{{ countOf(g.key) }}</span>
        <div class="nb-rule flex-spacer"></div>
      </div>
      <div class="scene-grid">
        <div
          v-for="s in byGroup(g.key)"
          :key="s.code"
          class="scene-card"
          :style="{ '--tab': g.color }"
          @click="router.push(routeOf(s))"
        >
          <div class="scene-code">{{ s.code }}</div>
          <div class="scene-body">
            <strong>{{ s.title }}</strong>
            <p>{{ s.desc }}</p>
          </div>
          <el-icon class="go"><ArrowRight /></el-icon>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowRight, Mouse, Timer, FullScreen, Monitor, Tools, Lock } from '@element-plus/icons-vue'
import { groups, scenarios, routeOf } from '../../data/scenarios'

const iconMap = { interact: Mouse, wait: Timer, window: FullScreen, compat: Monitor, misc: Tools, crypt: Lock }
const router = useRouter()
const byGroup = (key) => scenarios.filter((s) => s.group === key)
const countOf = (key) => scenarios.filter((s) => s.group === key).length

const goAnchor = (key) => {
  document.getElementById(key)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped>
.home { max-width: 1120px; margin: 0 auto; padding-bottom: 60px; }

/* ---------- 封面页 ---------- */
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 34px 38px 30px;
  border-radius: 6px 14px 14px 6px;
  color: var(--ink);
  background: var(--page);
  border: 1.5px solid var(--line);
  box-shadow: 0 18px 44px rgba(26, 26, 26, 0.16);
  position: relative;
  animation: nb-rise 0.7s ease both;
}
/* 纸页打孔 */
.hero::before {
  content: '';
  position: absolute;
  left: 14px;
  top: 26px;
  bottom: 26px;
  width: 14px;
  background-image: radial-gradient(circle at 7px 7px, var(--desk) 0 6px, transparent 6.5px);
  background-size: 14px 34px;
  background-repeat: repeat-y;
}
.hero-left { padding-left: 26px; }
.hero h1 {
  font-family: var(--font-serif);
  font-size: 34px;
  font-weight: 900;
  line-height: 1.28;
  letter-spacing: 2px;
  margin: 16px 0 8px;
}
.sub-en {
  margin: 0 0 10px;
  font-family: 'Bodoni Moda', Georgia, serif;
  font-style: italic;
  font-size: 15px;
  color: var(--muted);
  letter-spacing: 0.3px;
}
.hero-cn { margin: 0 0 16px; color: var(--ink-2); font-size: 13px; line-height: 1.9; }
.chips { display: flex; gap: 10px; flex-wrap: wrap; }

.hero-stat { display: flex; gap: 30px; flex: 0 0 auto; }
.hero-stat div { text-align: center; }
.hero-stat b {
  display: block;
  font-family: var(--font-serif);
  font-size: 30px;
  font-weight: 900;
  color: var(--ink);
}
.hero-stat span {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 1.5px;
  color: var(--muted);
}

/* ---------- 分类卡 ---------- */
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 20px 0 10px; }
.stat-card {
  background: var(--paper);
  border: 1.5px solid var(--line);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
}
.stat-card:hover {
  transform: translateY(-3px);
  border-color: var(--tab, var(--tab1));
  box-shadow: 0 10px 22px rgba(26, 26, 26, 0.1);
}
.sc-icon {
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1a1a1a;
  background: var(--tab, var(--tab1));
  box-shadow: 0 3px 8px rgba(26, 26, 26, 0.12);
}
.sc-meta { flex: 1; min-width: 0; }
.sc-meta strong {
  display: block;
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
}
.sc-meta span { font-size: 11.5px; color: var(--text-3); }
.sc-count { font-family: var(--font-mono); font-size: 11px; color: var(--text-3); white-space: nowrap; }

/* ---------- 场景分组 ---------- */
.group { margin-top: 30px; scroll-margin-top: 14px; }
.group-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.tab-piece {
  width: 12px;
  height: 30px;
  border-radius: 0 8px 8px 0;
  background: var(--tab, var(--tab1));
  box-shadow: 2px 2px 5px rgba(26, 26, 26, 0.12);
  flex: 0 0 auto;
}
.group-name {
  font-family: var(--font-serif);
  font-size: 19px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--ink);
  line-height: 1.4;
}
.group-count {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink);
  background: var(--tab, var(--tab1));
  border-radius: 20px;
  padding: 3px 10px;
  flex: 0 0 auto;
}

.scene-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.scene-card {
  background: var(--paper);
  border: 1.5px solid var(--line);
  border-radius: 12px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
}
.scene-card:hover {
  border-color: var(--tab, var(--tab1));
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(26, 26, 26, 0.1);
}
.scene-code {
  flex: 0 0 auto;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--ink);
  background: var(--tab, var(--tab1));
  border: 1px solid rgba(26, 26, 26, 0.08);
  padding: 4px 9px;
  border-radius: 7px;
}
.scene-body { flex: 1; min-width: 0; }
.scene-body strong { font-size: 14px; font-weight: 500; }
.scene-body p { margin: 3px 0 0; color: var(--text-3); font-size: 12px; line-height: 1.6; }
.go { color: var(--faint); flex: 0 0 auto; }
.scene-card:hover .go { color: var(--brand); }

@media (max-width: 1100px) {
  .cards { grid-template-columns: repeat(3, 1fr); }
  .scene-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
