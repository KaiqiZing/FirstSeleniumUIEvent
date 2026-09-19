// 场景目录单一数据源：同时驱动侧边导航、首页卡片与路由注册。

// 每组对应一枚「笔记本标签」配色（风格 A）
export const groups = [
  { key: 'interact', name: '页面交互类', desc: '高频交互陷阱', icon: 'Mouse', color: 'var(--tab1)' },
  { key: 'wait', name: '等待与响应类', desc: '慢接口与竞态', icon: 'Timer', color: 'var(--tab4)' },
  { key: 'window', name: '多窗口与多标签', desc: '句柄切换与弹窗', icon: 'FullScreen', color: 'var(--tab2)' },
  { key: 'compat', name: '浏览器兼容类', desc: '控件与运行环境', icon: 'Monitor', color: 'var(--tab5)' },
  { key: 'misc', name: '其他疑难类', desc: '验证码与会话', icon: 'Tools', color: 'var(--tab3)' },
  { key: 'crypt', name: '数据加密类', desc: '加密与密文核对', icon: 'Lock', color: 'var(--tab6)' }
]

const ROUTE_PREFIX = { interact: '/i', wait: '/w', window: '/m', compat: '/c', misc: '/x', crypt: '/e' }

export function routeOf(s) {
  // code 形如 'I-01'，取短横线后两位编号
  return ROUTE_PREFIX[s.group] + '/' + s.code.slice(2)
}

export function groupOf(key) {
  return groups.find((g) => g.key === key) || { key, name: key, desc: '' }
}

export const scenarios = [
  // ---------- 页面交互类 ----------
  { code: 'I-01', group: 'interact', file: '01-not-interactable', title: '元素不可交互', desc: '页面上存在看得见但无法点击/输入的提交控件。' },
  { code: 'I-02', group: 'interact', file: '02-click-intercepted', title: '点击被拦截', desc: '加载遮罩、固定头部或浮层覆盖在目标按钮之上。' },
  { code: 'I-03', group: 'interact', file: '03-stale-element', title: '元素引用失效', desc: '列表周期重渲染，操作过元素后引用随即失效。' },
  { code: 'I-04', group: 'interact', file: '04-iframe-nested', title: 'iframe 嵌套定位', desc: '业务入口嵌在双层框架中，操作需先切到框架上下文。' },
  { code: 'I-05', group: 'interact', file: '05-shadow-dom', title: 'Shadow DOM 控件', desc: '控件位于 Web Component 影子节点内部。' },
  { code: 'I-06', group: 'interact', file: '06-dynamic-attributes', title: '动态 ID / class', desc: '关键控件的属性每次刷新都会随机变化。' },
  { code: 'I-07', group: 'interact', file: '07-dropdowns', title: '两类下拉框', desc: '原生下拉与自定义下拉混在同一个筛选表单里。' },
  { code: 'I-08', group: 'interact', file: '08-hover-menu', title: '悬浮菜单', desc: '菜单仅在鼠标悬停时展开，移开即收起。' },
  { code: 'I-09', group: 'interact', file: '09-drag-drop', title: '拖拽排序', desc: '候选与已选区域支持鼠标拖拽搬运。' },
  { code: 'I-10', group: 'interact', file: '10-file-upload', title: '文件上传', desc: '选择本地文件后回显并提交到服务端。' },
  { code: 'I-11', group: 'interact', file: '11-native-dialogs', title: '原生弹窗', desc: '依次演示 alert / confirm / prompt 三类系统弹窗。' },
  { code: 'I-12', group: 'interact', file: '12-rich-text', title: '富文本编辑', desc: '在可编辑区域内排版文本后提交。' },
  { code: 'I-13', group: 'interact', file: '13-animation', title: '渐入动画', desc: '内容面板带淡入与位移动画，动画期间操作不稳定。' },
  { code: 'I-14', group: 'interact', file: '14-lazy-load', title: '滚动懒加载', desc: '长列表分页拉取，滚动到底才追加渲染。' },
  { code: 'I-15', group: 'interact', file: '15-coordinate-offset', title: '坐标偏移', desc: '页面容器被缩放变换，元素渲染位置与布局坐标不一致。' },
  { code: 'I-16', group: 'interact', file: '16-controlled-input', title: '受控输入与联想', desc: '搜索框异步联想、受控表单的值回填与清空场景。' },
  { code: 'I-17', group: 'interact', file: '17-parent-child-amount', title: '父子级金额勾稽', desc: '结算单父单折叠子单，父子同名金额列，调整后异步重算勾稽差额。' },
  { code: 'I-18', group: 'interact', file: '18-page-db-consistency', title: '页面数字与数据库核对', desc: '明细分页展示、库中以「分」存储、汇总字段与明细漂移，需比对页面数字与落库原始值。' },

  // ---------- 等待与响应类 ----------
  { code: 'W-01', group: 'wait', file: '01-slow-loading', title: '慢接口加载', desc: '查询接口响应较慢，期间出现全屏加载遮罩。' },
  { code: 'W-02', group: 'wait', file: '02-spa-route-switch', title: 'SPA 路由切换', desc: '页面在单页内切换，地址变化但浏览器无整页刷新。' },
  { code: 'W-03', group: 'wait', file: '03-export-task', title: '长任务导出', desc: '导出耗时约十秒，完成后提供下载链接。' },
  { code: 'W-04', group: 'wait', file: '04-race-assert', title: '保存后即时断言', desc: '点击保存后数据要一段时间才出现在列表里。' },
  { code: 'W-05', group: 'wait', file: '05-unstable-api', title: '不稳定接口', desc: '请求偶发失败、返回时快时慢，需要重试容错。' },

  // ---------- 多窗口与多标签 ----------
  { code: 'M-01', group: 'window', file: '01-new-tab', title: '新标签打开明细', desc: '点击记录后在新标签页打开业务详情。' },
  { code: 'M-02', group: 'window', file: '02-oauth-popup', title: '授权窗口回跳', desc: '第三方授权小窗，完成授权后自动关闭并回传结果。' },
  { code: 'M-03', group: 'window', file: '03-window-iframe', title: '新窗口内嵌框架', desc: '新开的窗口页面里还嵌套着 iframe 业务。' },
  { code: 'M-04', group: 'window', file: '04-popup-blocked', title: '非手势弹窗', desc: '脚本延迟触发的 window.open，受浏览器弹窗策略影响。' },

  // ---------- 浏览器兼容类 ----------
  { code: 'C-01', group: 'compat', file: '01-date-input', title: '日期时间控件', desc: '原生日期时间输入，各浏览器表现差异较大。' },
  { code: 'C-02', group: 'compat', file: '02-env-info', title: '运行环境信息', desc: '读取并展示浏览器环境与页面参数。' },

  // ---------- 其他疑难类 ----------
  { code: 'X-01', group: 'misc', file: '01-captcha', title: '图形验证码', desc: '登录环节需要先通过图形验证码校验。' },
  { code: 'X-02', group: 'misc', file: '02-bot-detection', title: '自动化特征检测', desc: '页面探测运行环境特征并据此限制部分能力。' },
  { code: 'X-03', group: 'misc', file: '03-cookie-session', title: '会话保持', desc: '登录后会话保存在浏览器侧，刷新与重开页面均需校验。' },
  { code: 'X-04', group: 'misc', file: '04-seed-data', title: '数据自造自销', desc: '工单数据先在后端生成，再在页面登记消费。' },

  // ---------- 数据加密类 ----------
  { code: 'E-01', group: 'crypt', file: '01-transport-encryption', title: '传输字段加密', desc: '表单值在页面上是明文，提交报文里已是 RSA 密文。' },
  { code: 'E-02', group: 'crypt', file: '02-masked-display', title: '敏感字段脱敏', desc: '列表只展示掩码，完整值需单独申请且限时可见。' },
  { code: 'E-03', group: 'crypt', file: '03-cipher-storage', title: '密文存储核对', desc: '库中为 AES 密文与多版本密钥，页面展示的是解密结果。' },
  { code: 'E-04', group: 'crypt', file: '04-response-encryption', title: '报文加密签名', desc: '接口整体返回密文，需本地解密并校验时间戳与签名。' }
]
