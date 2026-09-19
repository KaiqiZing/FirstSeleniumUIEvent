<template>
  <div class="page">
    <div class="page-title">客户分级运营</div>
    <p class="page-desc">顶部一级菜单与行内操作均采用悬浮交互，悬停后才会展开对应操作区。</p>

    <section class="panel">
      <h3>运营菜单</h3>
      <p class="p-sub">将鼠标移动到「运营动作」上会展开子菜单，移出后子菜单收起。</p>

      <div class="demo-nav">
        <span class="nav-item plain">工作台</span>
        <span class="nav-item plain">客户列表</span>
        <div class="nav-item drop">
          <span class="drop-trigger">运营动作</span>
          <div class="drop-menu">
            <button type="button" @click="menuAction('批量标签')">批量打标签</button>
            <button type="button" @click="menuAction('营销活动')">发起营销活动</button>
            <button type="button" @click="menuAction('对账复核')">对账复核</button>
            <button type="button" @click="menuAction('规则设置')">规则设置</button>
          </div>
        </div>
        <span class="nav-item plain">数据看板</span>
      </div>
    </section>

    <section class="panel">
      <h3>客户行操作</h3>
      <p class="p-sub">鼠标悬停到某一行的行身上，该行末尾才会出现操作按钮。</p>

      <div class="c-table">
        <div class="c-head">
          <span style="width: 130px">客户编号</span>
          <span style="flex: 1">客户名称</span>
          <span style="width: 100px">等级</span>
          <span style="width: 180px">操作</span>
        </div>
        <div
          v-for="r in customers"
          :key="r.no"
          class="c-row"
          @mouseenter="hoverNo = r.no"
          @mouseleave="hoverNo = ''"
        >
          <span style="width: 130px" class="mono">{{ r.no }}</span>
          <span style="flex: 1">{{ r.name }}</span>
          <span style="width: 100px">{{ r.level }}</span>
          <span style="width: 180px" class="row-actions">
            <template v-if="hoverNo === r.no">
              <button type="button" @click="rowAction(r, '编辑资料')">编辑</button>
              <button type="button" @click="rowAction(r, '发放优惠券')">发券</button>
              <button type="button" class="danger" @click="rowAction(r, '停用')">停用</button>
            </template>
            <span v-else class="placeholder">—</span>
          </span>
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

const hoverNo = ref('')
const logs = ref([])
const stamp = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

const customers = [
  { no: 'C-88121', name: '上海恒隆商贸有限公司', level: '金牌' },
  { no: 'C-88122', name: '杭州瑞品电子商务有限公司', level: '银牌' },
  { no: 'C-88123', name: '深圳前海集采供应链', level: '金牌' },
  { no: 'C-88124', name: '成都天虹零售连锁', level: '普通' }
]

function menuAction(name) {
  logs.value.unshift({ time: stamp(), text: `菜单动作：执行「${name}」` })
}

function rowAction(row, action) {
  logs.value.unshift({ time: stamp(), text: `客户 ${row.name}：执行「${action}」` })
}
</script>

<style scoped>
.demo-nav {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--brand-soft);
  border: 1px solid var(--brand-line);
  border-radius: 8px;
  padding: 6px 8px;
}
.nav-item {
  padding: 7px 14px;
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-1);
  cursor: default;
}
.nav-item.plain { cursor: pointer; }
.nav-item.plain:hover { background: var(--brand-soft); color: var(--brand-2); }
.drop { position: relative; }
.drop-trigger { cursor: pointer; padding: 7px 14px; border-radius: 6px; }
.drop:hover .drop-trigger, .drop-trigger:hover { background: var(--brand-soft); color: var(--brand-2); }
.drop-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 140px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(31, 35, 41, 0.12);
  padding: 6px;
  display: none;
  z-index: 8;
}
.drop:hover .drop-menu { display: flex; flex-direction: column; }
.drop-menu button {
  border: 0;
  background: transparent;
  text-align: left;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-1);
}
.drop-menu button:hover { background: var(--brand-soft); color: var(--brand-2); }

.c-table { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.c-head, .c-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  font-size: 13px;
}
.c-head { background: var(--paper); color: var(--text-3); }
.c-row { border-top: 1px solid var(--border); }
.c-row:hover { background: var(--brand-soft); }
.row-actions { display: flex; gap: 6px; }
.row-actions button {
  border: 1px solid var(--brand);
  background: #fff;
  color: var(--brand);
  border-radius: 5px;
  padding: 3px 10px;
  font-size: 12px;
  cursor: pointer;
}
.row-actions button:hover { background: var(--brand-soft); }
.row-actions button.danger { border-color: var(--danger); color: var(--danger); }
.row-actions button.danger:hover { background: #fbeff0; }
.placeholder { color: #c4bfae; }
</style>
