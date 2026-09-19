<template>
  <div class="layout">
    <aside class="side">
      <div class="brand">
        <div class="logo">S</div>
        <div class="brand-meta">
          <strong>UI 场景演练台</strong>
          <em>Web 自动化问题复现</em>
        </div>
      </div>

      <nav class="nav">
        <template v-for="g in groups" :key="g.key">
          <div class="group-title">{{ g.name }}</div>
          <div
            v-for="s in byGroup(g.key)"
            :key="s.code"
            class="item"
            :class="{ active: isActive(s) }"
            :style="{ '--tab': g.color }"
            @click="router.push(routeOf(s))"
          >
            <span class="code">{{ s.code }}</span>
            <span class="name">{{ s.title }}</span>
          </div>
        </template>
      </nav>

      <div class="side-foot">仅复现问题现象<br />页面不含操作提示</div>
    </aside>

    <div class="wrap">
      <header class="topbar">
        <div class="crumb home" @click="router.push('/')">
          <el-icon :size="15"><HomeFilled /></el-icon>
          <span>首页</span>
        </div>
        <template v-if="cur">
          <span class="sep">/</span>
          <span class="crumb-code mono">{{ cur.code }}</span>
          <span class="crumb-title">{{ cur.title }}</span>
          <span class="crumb-path mono">{{ cur.route }}</span>
        </template>
        <div class="flex-spacer"></div>
        <div v-if="cur" class="env">
          <span class="group-tag" :style="{ '--tab': cur.color }">{{ cur.groupName }}</span>
        </div>
      </header>
      <div class="topbar-rule" aria-hidden="true"></div>

      <main class="content">
        <!-- 风格 A 装饰：左侧打孔 + 右侧标签条（不拦截点击） -->
        <div class="holes" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
        <div class="edge-tab" aria-hidden="true" :style="{ '--tab': curTabColor }">
          <span>{{ cur ? cur.groupName : 'SCENARIOS' }}</span>
        </div>

        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled } from '@element-plus/icons-vue'
import { groups, scenarios, routeOf, groupOf } from '../data/scenarios'

const route = useRoute()
const router = useRouter()

const byGroup = (key) => scenarios.filter((s) => s.group === key)

const cur = computed(() => {
  const m = route.meta
  if (!m || !m.code) return null
  const g = groupOf(m.group)
  return {
    code: m.code,
    title: m.title,
    route: route.path,
    groupName: g.name,
    color: g.color || 'var(--tab1)'
  }
})

const curTabColor = computed(() => cur.value?.color || 'var(--tab1)')

const isActive = (s) => route.path === routeOf(s)
</script>

<style scoped>
.layout {
  display: flex;
  height: 100%;
  background: var(--desk);
}

/* ---------------- 侧边：墨色笔记本封面 ---------------- */
.side {
  width: 240px;
  flex: 0 0 240px;
  background: linear-gradient(180deg, var(--bg-side), var(--bg-side-2));
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow: 6px 0 24px rgba(26, 26, 26, 0.18);
  position: relative;
  z-index: 2;
}
/* 书脊压线 */
.side::after {
  content: '';
  position: absolute;
  right: 6px;
  top: 0;
  bottom: 0;
  width: 1px;
  background: repeating-linear-gradient(180deg, rgba(255, 255, 255, 0.16) 0 10px, transparent 10px 22px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 16px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.logo {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--tab1), #6fbfa2);
  color: #1a1a1a;
  font-family: var(--font-serif);
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 19px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}
.brand-meta strong {
  display: block;
  color: #f8f6f1;
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 1px;
}
.brand-meta em {
  font-style: normal;
  font-family: var(--font-mono);
  font-size: 10.5px;
  letter-spacing: 1px;
  color: rgba(248, 246, 241, 0.45);
}

.nav { flex: 1; padding: 8px 10px 16px; }
.group-title {
  color: rgba(248, 246, 241, 0.42);
  font-family: var(--font-mono);
  font-size: 10.5px;
  letter-spacing: 2px;
  text-transform: uppercase;
  padding: 16px 10px 6px;
}
.item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 10px;
  border-radius: 4px 10px 10px 4px;
  color: rgba(248, 246, 241, 0.72);
  cursor: pointer;
  margin-bottom: 2px;
  transition: background 0.16s ease, color 0.16s ease, transform 0.16s ease;
}
.item:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
.item.active {
  background: var(--tab, var(--tab1));
  color: #1a1a1a;
  font-weight: 500;
  transform: translateX(2px);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}
.code {
  font-family: var(--font-mono);
  font-size: 11px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.14);
  padding: 2px 6px;
  border-radius: 5px;
  flex: 0 0 auto;
}
.item.active .code { background: rgba(26, 26, 26, 0.14); border-color: rgba(26, 26, 26, 0.22); }
.name { font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.side-foot {
  padding: 12px 16px;
  color: rgba(248, 246, 241, 0.3);
  font-family: var(--font-mono);
  font-size: 10.5px;
  line-height: 1.8;
  letter-spacing: 0.5px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

/* ---------------- 顶栏：纸页页眉 ---------------- */
.wrap { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.topbar {
  height: 54px;
  background: var(--page);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 24px;
  flex: 0 0 auto;
  border-bottom: 1px solid var(--line);
}
.topbar-rule {
  height: 2px;
  flex: 0 0 auto;
  background: repeating-linear-gradient(90deg, var(--line) 0 14px, transparent 14px 26px);
  opacity: 0.7;
}
.crumb { display: flex; align-items: center; gap: 6px; color: var(--text-2); cursor: pointer; font-size: 13px; }
.crumb.home:hover { color: var(--brand); }
.sep { color: var(--faint); }
.crumb-code {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--tab1);
  background: #1a1a1a;
  padding: 3px 8px;
  border-radius: 4px;
}
.crumb-title {
  font-family: var(--font-serif);
  font-weight: 700;
  color: var(--ink);
  font-size: 15px;
  letter-spacing: 0.5px;
}
.crumb-path { color: var(--faint); font-size: 12px; }
.env .group-tag {
  font-size: 12px;
  color: #1a1a1a;
  background: var(--tab, var(--tab1));
  border: 1px solid rgba(26, 26, 26, 0.08);
  padding: 3px 12px;
  border-radius: 20px;
  box-shadow: 0 2px 5px rgba(26, 26, 26, 0.08);
}

/* ---------------- 内容：纸张正文区 ---------------- */
.content {
  flex: 1;
  overflow-y: auto;
  padding: 22px 26px 0;
  position: relative;
  background-color: var(--page);
  /* 笔记本横格线 */
  background-image: repeating-linear-gradient(
    180deg,
    transparent 0 33px,
    rgba(200, 194, 178, 0.32) 33px 34px
  );
}

/* 左侧打孔 */
.holes {
  position: absolute;
  left: 10px;
  top: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  pointer-events: none;
  z-index: 0;
}
.holes i {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--desk);
  box-shadow: inset 0 2px 3px rgba(26, 26, 26, 0.28), 0 1px 0 rgba(255, 255, 255, 0.6);
}

/* 右侧标签条 */
.edge-tab {
  position: absolute;
  right: 0;
  top: 130px;
  width: 38px;
  padding: 16px 0;
  border-radius: 10px 0 0 10px;
  background: var(--tab, var(--tab1));
  color: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  box-shadow: -2px 2px 8px rgba(26, 26, 26, 0.12);
  z-index: 0;
}
.edge-tab span {
  writing-mode: vertical-rl;
  font-family: var(--font-sans);
  font-size: 12.5px;
  letter-spacing: 4px;
  white-space: nowrap;
}

.content > :deep(.page),
.content > :deep(.home) { position: relative; z-index: 1; }

@media (max-width: 1320px) {
  .holes, .edge-tab { display: none; }
}
</style>
