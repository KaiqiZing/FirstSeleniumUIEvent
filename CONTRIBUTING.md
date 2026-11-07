# 贡献指南

**简体中文** | [English](./CONTRIBUTING.en.md)

感谢你愿意为「UI 自动化问题场景演练台」出一份力。本项目是面向 Selenium Web UI 自动化的**练习靶场**：页面负责忠实还原真实系统里的故障现象，答案只写在 `README.md`，两边严格分离。

## 一、参与方式

| 类型 | 适合做的事 |
| --- | --- |
| 报告问题 | 某个场景复现不出来、页面报错、脚本断言口径有歧义 |
| 新增场景 | 补充 `README.md` 中尚未覆盖的高频问题（先开 Issue 对齐） |
| 改进文档 | 修正复现步骤、补齐接口契约、补充「不可复现项」说明 |
| 打磨平台 | 前端样式、导航结构、后端稳定性等非场景类改动 |

## 二、报告问题（Issue）

请在 Issue 中提供：

1. **出问题的路由**，例如 `/i/17`、`/e/03`。
2. **环境**：操作系统、浏览器与版本、WebDriver 版本、Node / Python 版本。
3. **复现步骤**与**预期 / 实际结果**（「操作结果」区域的日志文本最有用）。
4. 相关截图或控制台报错。

请勿在 Issue 中粘贴真实业务数据、内部系统地址或凭据；本项目的示例数据均为虚构。

## 三、提交代码（Pull Request）

```bash
# 1. Fork 后在本地开发
git clone https://github.com/<your-name>/FirstSeleniumUIEvent.git
cd FirstSeleniumUIEvent

# 2. 建分支（feat / fix / docs / chore 前缀）
git checkout -b feat/scenario-i19

# 3. 本地自测后提交
git add .
git commit -m "feat: 新增 I-19 场景（表格内嵌滚动）"

# 4. 推送并开 PR
git push origin feat/scenario-i19
```

PR 要求：

- 一个 PR 只做一件事，避免把格式化、重构、新场景混在一起。
- 提交前请确认前后端都能启动（`python app.py` / `npm run dev`），涉及构建配置的改动需 `npm run build` 通过。
- 在 PR 描述中写明：改动点、影响的场景编号、自测方式。

提交信息建议使用 Conventional Commits：`feat:` 新增场景或功能、`fix:` 修缺陷、`docs:` 文档、`chore:` 杂项、`refactor:` 重构。

## 四、新增一个场景需要同步的四处

以新增 `I-19` 为例，缺任何一处都会出现「导航有入口但页面 404」或「页面存在但文档无说明」：

1. **场景目录**：`frontend/src/data/scenarios.js`
   在对应分组的 `scenarios` 数组里追加 `{ code, group, file, title, desc }`。该文件是导航、首页卡片与路由注册的**唯一数据源**。
2. **页面组件**：`frontend/src/views/<group>/<file>.vue`
   `file` 命名与目录风格保持一致（如 `19-nested-scroll.vue`）。
3. **后端接口**（如需要）：`backend/api/xxx_api.py`
   新建 `Blueprint` 后必须在 `backend/api/__init__.py` 的 `register_blueprints` 中注册，统一挂载在 `/api` 前缀下。
4. **文档**：本项目维护中英两份 README，**两份必须同步修改**，否则内容会分叉：
   - [README.zh-CN.md](./README.zh-CN.md)（中文）与 [README.md](./README.md)（English）。
   - 各自第二节「场景总览」表格加一行。
   - 各自第三节补充「复现步骤 + Selenium 解决要点」。
   - 若新增接口，同步第四节「后端接口契约」。

## 五、编码约定

### 前端

- Vue 3 `<script setup>` + Element Plus，勿引入新的 UI 框架或状态管理库。
- 样式使用组件内 `scoped` 或 `src/styles` 中的公共变量，避免写全局选择器污染其他场景。
- **页面内不得出现任何解法提示、元素定位建议或「标准答案」文案**；现象要看起来像真实系统，而不是教学页。
- 操作结果统一输出到页面底部的「操作结果」区域（日志/状态文本），Selenium 脚本以此作为断言锚点。不要只依赖自动消失的 `ElMessage` 提示。

### 后端

- 统一响应体：`{ "code": 0, "data": ..., "message": "..." }`，`code=0` 表示成功；业务错误码在 README 中登记。
- 延迟、超时、失败率、分页大小等可调参数一律收敛到 `backend/config.py`，不要在业务代码里散落魔法数字。
- 数据结构保持可重复练习：内存态或可 `reset` 的 SQLite 表；重启 Flask 回到初始状态是设计目标，不是缺陷。
- 新增依赖请写入 `backend/requirements.txt`，前端依赖写入 `frontend/package.json`。

### 命名与编号

- 场景编号沿用现有分组前缀：`I-` 交互、`W-` 等待、`M-` 多窗口、`C-` 兼容、`X-` 其他、`E-` 加密；编号一经使用不复用、不跳号插队。
- 路由由 `group` 与 `code` 自动推导（如 `I-19` → `/i/19`），无需手写路由表。

## 六、不要提交的内容

以下内容已在 `.gitignore` 中忽略，请勿强制添加：

- `backend/data/`（SQLite 数据库，首次启动自动重建）
- `.venv/`、`backend/.SeleniumUIEvent/`、`__pycache__/`、`*.pyc`
- `node_modules/`、`frontend/dist/`
- `*.log`、`.env`、`.DS_Store`、`.idea/`、`.vscode/`

## 七、许可

本项目采用 [MIT License](./LICENSE)。提交 PR 即表示你同意你的贡献以相同许可发布。
