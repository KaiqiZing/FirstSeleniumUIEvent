# Selenium 自动化项目常见技术问题汇总

> 面向页面 UI 自动化（Web 端），按「页面交互 / 等待响应 / 浏览器兼容 / 多窗口切换 / 其他疑难」五大类整理，问题现象 + 原因 + 解决方案。

---

## 一、页面交互类问题（最高频）

### 1. ElementNotInteractableException（元素不可交互）
- **现象**：元素明明定位到了，点击/输入时报不可交互。
- **原因**：元素 `display:none`、`visibility:hidden`、尺寸为 0、disabled，或在可视区域外。
- **解决**：
  - 用显式等待等它「可见且可点击」：`element_to_be_clickable`，而不是只等「存在」；
  - 先滚动到可视区：`driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)`；
  - 检查前置条件（比如先展开折叠面板、先勾选项才激活按钮）。

### 2. ElementClickInterceptedException（点击被拦截）
- **现象**：其他元素会先接收到点击。
- **原因**：loading 遮罩、弹层、固定头部/底部、气泡提示挡住了目标元素。
- **解决**：
  - 等遮罩消失：`invisibility_of_element_located`；
  - 滚动避开固定导航遮挡（scrollIntoView 用 `block:'center'`）；
  - 兜底用 JS 点击（绕过事件层校验，谨慎使用，可能跳过前端逻辑）：
    `driver.execute_script("arguments[0].click();", el)`；
  - 或用 `ActionChains(driver).move_to_element(el).click().perform()`。

### 3. StaleElementReferenceException（元素引用失效）
- **现象**：第一次操作成功，隔一会再操作同一个元素对象就报错。
- **原因**：页面局部刷新 / React/Vue 重新渲染后，DOM 节点被重建，旧引用指向的节点已不在文档里。
- **解决**：
  - 不要长期缓存 WebElement，**用一次找一次**；
  - 显式等待旧元素失效：`EC.staleness_of(old_el)` 再重新定位；
  - 列表循环中先取数量，再按 index 每次重新 find；
  - 用 PageFactory/@FindBy 时注意它的缓存策略。

### 4. iframe 嵌套导致定位失败
- **现象**：元素在页面上肉眼可见，但 `find_element` 就是找不到（NoSuchElement）。
- **原因**：元素在 iframe/frame 内，driver 上下文还在主文档。
- **解决**：
  - `driver.switch_to.frame(frame元素或index或name)`；
  - 操作完退回：`driver.switch_to.default_content()`（回主文档）或 `parent_frame()`（回上一层）；
  - 多层嵌套要逐层切入；**iframe 是最常见的"定位不到"元凶，排查清单第一项**。

### 5. Shadow DOM 无法定位
- **现象**：CSS/XPath 都写对了，就是找不到，元素在 DevTools 里显示在 `#shadow-root` 下。
- **原因**：Shadow DOM 是封闭子树，普通选择器穿不透。
- **解决**：
  - JS 穿透：
    ```python
    host = driver.find_element(By.CSS_SELECTOR, "my-component")
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", host)
    btn = shadow_root.find_element(By.CSS_SELECTOR, "button")
    ```
  - Selenium 4 可直接用 `host.shadow_root`；
  - 多层 shadow 要逐层穿。

### 6. 动态 ID / 动态 class（前端框架生成）
- **现象**：今天能跑明天不能跑，ID 类似 `ext-gen1234`、class 类似 `css-1a2b3c` 每次发版都变。
- **解决**：
  - 放弃全量 ID，改用**稳定属性**：`name`、`type`、`placeholder`、`data-testid`（推动前端加）；
  - 用文本定位：`//button[text()='提交']`、`contains(@class,'submit-btn')` 取不变部分；
  - 相对定位：先锚定稳定的父级/兄弟元素再往下找。

### 7. 下拉框两类坑
- **原生 `<select>`**：用 `Select` 类，`select_by_visible_text / value / index`。
- **div+ul 假下拉（ElementUI/AntD 等）**：Select 类无效，必须「先点击展开 → 等选项出现 → 再点击选项」，选项常被渲染在 body 末尾（popper），别在父容器里找。

### 8. 悬浮（hover）菜单
- **现象**：菜单只有鼠标悬停才出现。
- **解决**：`ActionChains(driver).move_to_element(menu).perform()`，然后显式等待子菜单出现再点；注意子菜单在鼠标移走后立即消失，动作要连贯，必要时 `move_to_element(sub).click().perform()` 一气呵成。

### 9. 拖拽
- 普通拖拽：`ActionChains.drag_and_drop(src, dst)` 或 `click_and_hold → move_to_element → release`。
- **HTML5 原生拖拽（dragstart/drop 事件）**：ActionChains 经常无效，需注入 JS 模拟 DataTransfer 事件。

### 10. 文件上传
- **`input[type=file]`**：直接 `send_keys(绝对路径)`，最简单可靠（哪怕 input 隐藏也可以先 JS 改可见）。
- **系统级文件对话框（非 input 触发）**：Selenium 管不了，方案：
  - 优先找页面是否有隐藏 input 可直接 send_keys；
  - Windows 上用 pywinauto / AutoIt 操作系统对话框；
  - 改造测试策略：上传走接口造数，UI 只验证展示。

### 11. 弹窗 Alert / Confirm / Prompt
- 原生 JS 弹窗：`driver.switch_to.alert`，`accept() / dismiss() / send_keys()`；**注意它会阻塞 JS，不用显式等待找元素的方式等它，用 `EC.alert_is_present()`**。
- 页面自定义弹窗（div 模拟）：按普通元素处理，别用 switch_to.alert。

### 12. 富文本编辑器（contenteditable / iframe 内编辑器）
- 普通 send_keys 可能进不去或格式错乱；
- 方案：先点击编辑区获取焦点再 send_keys；或在 iframe 里的先切 frame；实在不行 JS 设置 `innerHTML` + 触发 input 事件。

### 13. 元素动画 / 渐入渐出
- 元素出现但还在移动/半透明中，点击坐标算错或点到旧位置；
- 解决：等动画完成（等某个 class 变化 / 固定小延时 / 等元素位置稳定两次坐标一致）。

### 14. 滚动与懒加载
- 长列表懒加载：需要**循环滚动到底部**并等待新数据渲染，直到数量不再增长；
- 元素在可视区外某些框架不渲染（虚拟列表），定位前必须滚动使其渲染。

### 15. 点击坐标偏移
- 高 DPI 屏幕 / 浏览器缩放 ≠ 100% / 窗口未最大化，导致 move_to 坐标偏移；
- 解决：测试机固定 100% 缩放、启动参数 `--force-device-scale-factor=1`、用 `scrollIntoView` 后用元素点击而非坐标点击。

### 16. send_keys 输入问题
- **中文输入**：直接 send_keys 中文一般可用，但触发不了输入法联想类组件（搜索建议），需要逐字输入 + 等待建议列表；
- **React/Vue 受控组件**：JS 直接改 value 不触发框架状态更新，后续校验不通过——要用 send_keys 真实键入，或 JS 改值后手动派发 `input/change` 事件；
- **输入内容被清空**：前置 JS 校验或 placeholder 干扰，先 `clear()` 再输入，必要时 `send_keys(Keys.CONTROL+'a') + DELETE`。

---

## 二、等待与响应类问题

### 1. 三种基础等待方式对比
| 方式 | 写法 | 优点 | 缺点 |
|---|---|---|---|
| 强制等待 sleep | `time.sleep(3)` | 简单粗暴 | 不管元素好不好都等满，用例慢；环境一慢还是失败 |
| 隐式等待 | `driver.implicitly_wait(10)` | 全局生效，一次设置 | 只管 find_element 的「存在」，不管可见/可点击；与显式等待混用会叠加超时 |
| 显式等待 | `WebDriverWait(driver,10).until(EC.xxx)` | 精确到条件，最快响应 | 每个点都要写，代码量大 |

**实践建议**：以显式等待为主，隐式等待给一个小值（或干脆不设），封装统一的等待工具方法。

### 2. 常用 expected_conditions 速查
- `presence_of_element_located`：DOM 里存在（不一定可见）
- `visibility_of_element_located`：可见
- `element_to_be_clickable`：可见且可点（点击前必用）
- `invisibility_of_element_located`：消失（等 loading 遮罩）
- `text_to_be_present_in_element`：文本出现（等数据回填）
- `staleness_of`：旧元素失效
- `url_contains / title_is`：页面跳转完成
- `alert_is_present`：弹窗出现

### 3. 流式等待 Fluent Wait
`WebDriverWait(driver, 20, poll_frequency=0.5, ignored_exceptions=[NoSuchElementException])`——自定义轮询频率与忽略异常，适合响应不稳定的场景。

### 4. sleep 的典型坑
- 本地能跑、CI 上挂（机器慢）；或者测试环境接口慢，固定 3 秒不够；
- 大量 sleep 叠加让整套用例从 20 分钟变 2 小时；
- **规则：sleep 只用于「没有可等待条件的场景」（如动画），且尽量封装成小函数控制总时长**。

### 5. 页面加载策略 pageLoadStrategy
- `normal`（默认）：等所有资源（图片、CSS、JS）加载完——慢站点卡死你；
- `eager`：DOM ready 就返回；
- `none`：导航立即返回，自己等。
- 对慢站点建议 eager/none + 自己等关键元素，能省大量时间。

### 6. 等待「页面真正渲染完」的补充手段
- `document.readyState == 'complete'`；
- jQuery 站点等 `jQuery.active == 0`（Ajax 全部结束）；
- SPA 等接口：轮询 `performance.getEntries()` 或抓 XHR 状态；
- 等 loading 图标消失比等「目标元素出现」更稳——很多页面元素先在、数据后到。

### 7. SPA（前后端分离）路由切换无刷新
- Vue/React 单页应用切页不触发浏览器导航，url 变化但 readyState 不动；
- 解决：等 `url_contains` + 新页面标志性元素可见，双条件。

### 8. 超时体系要分层
| 层级 | 建议 |
|---|---|
| 找元素 | 显式等待 10s 左右 |
| 页面加载 | `set_page_load_timeout(30)` |
| 脚本执行 | `set_script_timeout(30)` |
| 业务长操作（导出、批量） | 单独大超时 60~300s，用自定义轮询 |

### 9. 竞态问题（点击后立刻断言失败）
- 点了保存马上断言列表有新数据——接口还没回来；
- 解决：断言本身也放进 WebDriverWait 里轮询（如自研 `wait_until_text_appears`），而不是断言前加 sleep。

### 10. 接口慢 / 数据渲染慢
- 自定义 expected condition：等某个元素文本非空、等列表行数 ≥ N；
- 终极方案：UI 等待 + 接口/数据库轮询结合，确认后端数据已生成再等前端展示。

---

## 三、浏览器兼容性测试

### 1. 兼容性矩阵
- 主流：**Chrome、Edge、Firefox**（Windows）；**Safari**（Mac，仅 macOS 可跑 safaridriver）；
- 金融/政企客户还可能要求国产浏览器（360 极速、奇安信等，多为 Chromium 内核，可用 ChromeDriver 指定 binary 跑）；
- 建议按客户实际使用环境定矩阵，不必全测，核心用例跑全矩阵、全量用例跑主浏览器。

### 2. Driver 与浏览器版本匹配（最大的坑）
- Chrome 自动升级导致 ChromeDriver 不匹配，整套用例直接起不来；
- 方案：
  - Chrome 115+ 用官方 Chrome for Testing（CfT）下载匹配版本；
  - Selenium 4.6+ 自带 Selenium Manager 自动下载匹配 driver，尽量升级 Selenium 版本；
  - CI 上锁定浏览器版本（Docker 镜像固化），禁止自动更新。

### 3. 分布式/并行执行兼容性用例
- Selenium Grid / Selenoid / docker-selenium：一套用例按 browser 参数化分发到不同节点；
- pytest 参数化示例：`pytest --browser=chrome` / `--browser=firefox`，fixture 里按参数建 driver。

### 4. Headless（无头）与有头差异
- headless 下窗口默认尺寸小、无 GPU 渲染，hover、动画、截图、文件下载行为可能不同；
- 解决：headless 必须显式 `--window-size=1920,1080`；新版用 `--headless=new`；下载目录、弹窗行为单独验证；关键用例保留有头模式巡检。

### 5. 各浏览器行为差异点（用例容易踩）
| 差异点 | 说明 |
|---|---|
| 日期/时间控件 | Chrome 原生日期控件输入方式与 Firefox 完全不同，常需 JS 赋值 |
| 滚动条 | Firefox 滚动事件触发时机不同；Mac 滚动条悬浮不占位 |
| 文件路径 | Windows `\` vs Mac/Linux `/`，上传路径要用 os.path.join |
| 弹窗/下载 | 各浏览器下载行为、是否弹保存框不同，用 capability 配置静默下载 |
| CSS 渲染 | 字体、行高差异导致元素换行、遮挡（兼容性截图比对很有必要） |
| JS 引擎 | 个别语法/Intl 行为差异，页面报 JS 错导致功能失效 |

### 6. 分辨率 / DPI / 缩放
- 不同机器缩放比例（125%、150%）导致坐标类操作偏移、元素被挤出视口；
- 统一：CI 固定分辨率 1920×1080、缩放 100%、`--force-device-scale-factor=1`。

### 7. IE 退役后的 Edge IE 模式
- 老政企系统只支持 IE：可用 Edge 的 IE 兼容模式 + IEDriverServer 配置 `ie.edgechromium=true`；但微软已逐步禁用，建议推动系统改造，别在 IE 模式上长期投入。

### 8. 移动端 H5 兼容性
- 用 Chrome DevTools 设备模拟：`mobileEmulation: {deviceName: 'iPhone X'}`；
- 或接真机云测平台（Appium 路线），Selenium 只做模拟器级别验证。

### 9. 统一 capability 配置
- 把浏览器类型、版本、headless、窗口尺寸、下载目录、acceptInsecureCerts 全部收敛到一个工厂类/conftest，避免散落在用例里。

---

## 四、多窗口 / 多标签页切换

### 1. 基本概念
- `driver.current_window_handle`：当前窗口句柄；
- `driver.window_handles`：所有窗口句柄列表；
- `driver.switch_to.window(handle)`：切换。

### 2. 新窗口/新标签页的标准切换姿势
```python
old = driver.current_window_handle
driver.find_element(...).click()  # 触发打开新窗口
WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
for h in driver.window_handles:
    if h != old:
        driver.switch_to.window(h)
```
**不要简单取 `window_handles[-1]`**——多窗口并存时顺序不可靠，更稳的写法是按 title 或 url 循环匹配：
```python
for h in driver.window_handles:
    driver.switch_to.window(h)
    if "目标标题" in driver.title:
        break
```

### 3. Selenium 4 新 API
`driver.switch_to.new_window('tab')` / `new_window('window')` 直接开新标签并切过去。

### 4. NoSuchWindowException（句柄失效）
- **现象**：窗口被业务关闭后，driver 还指向它，后续任何操作报错；
- 解决：`close()` 当前窗口后**必须** `switch_to.window(剩余句柄)`；操作前校验句柄是否还在 `window_handles` 里。

### 5. 弹窗型窗口（OAuth 登录、支付页）
- 第三方登录弹小窗：切进去完成授权 → 弹窗自动关闭 → 切回主窗口句柄（提前存好）；
- 注意有些浏览器把 `target=_blank` 开成新 tab、有些开成新 window，处理逻辑一样。

### 6. window 和 iframe 别搞混
- iframe 用 `switch_to.frame`，新窗口用 `switch_to.window`，两套体系互不通用；
- 排查"定位不到"时两个方向都要查：既可能在 iframe 里，也可能在新窗口里。

### 7. 多窗口 + iframe 组合
- 切到新窗口后，frame 上下文是独立的，需要重新 switch_to.frame；
- 切回主窗口后用 `default_content()` 复位。

### 8. 弹窗拦截
- 非用户手势触发的 `window.open` 可能被浏览器拦截（handles 数量不增加）；
- 解决：capability 关闭弹窗拦截（Chrome: `--disable-popup-blocking`）。

---

## 五、其他高频疑难问题（杂项汇总）

### 1. 验证码
- 原则：**测试环境让开发提供万能验证码或开关**，这是正路；
- 备选：OCR 识别（简单图形码，ddddocr）、打码平台（滑块/点选）、cookie 注入跳过登录、session 复用（先手工登录一次导出 cookie，后续 add_cookie 直接进入）。

### 2. 反爬 / Bot 检测
- 站点检测 `navigator.webdriver=true` 拒绝服务或弹人机验证；
- 方案：CDP 注入隐藏特征 `Page.addScriptToEvaluateOnNewDocument` 改 webdriver 属性；Chrome option `excludeSwitches=['enable-automation']`；或用 undetected-chromedriver（注意合规，仅用于自有系统测试）。

### 3. 用例不稳定（Flaky Test）——自动化最大的成本
- 治理手段：
  - 失败自动重试（pytest-rerunfailures，最多 2 次，重试要统计上报，不能掩盖问题）；
  - **失败自动截图 + 当前 URL + 页面源码留存**，不然无法定责；
  - 分层归因：环境脏数据 / 等待不充分 / 前端发版改样式 / 脚本本身 bug，建失败原因台账；
  - 定期清理 flaky 用例排行榜，要么修要么降级。

### 4. CI/流水线环境差异
- Linux 无显示服务器：必须 headless 或配 Xvfb；
- 中文字体缺失导致截图对比失败、元素宽度不同——CI 镜像装中文字体；
- 时区/语言：镜像默认 UTC + en-US，日期断言会挂，设 `TZ=Asia/Shanghai`、`--lang=zh-CN`；
- 容器内存小，Chrome 崩溃：`--disable-dev-shm-usage --no-sandbox`。

### 5. 文件下载验证
- 配置静默下载目录（Chrome: `download.default_directory` + `download.prompt_for_download=false`）；
- 下载完成判断：轮询目录中无 `.crdownload` 临时文件；
- headless 老版本不支持下载，新版需 CDP `Page.setDownloadBehavior`。

### 6. Cookie / 缓存 / 无痕
- 用例间串数据：每条用例前 `delete_all_cookies()` 或每次全新 driver（推荐后者，隔离彻底）；
- 验证"记住我"类功能时反过来，需要显式保留 profile。

### 7. HTTPS 证书问题
- 测试环境自签名证书拦安全警告：`accept_insecure_certs=True`（Selenium 4 标准 capability），老写法 `acceptSslCerts` 已废弃。

### 8. 代理抓包
- 需要抓包验证请求时挂浏览器代理（`--proxy-server`）；公司内网代理导致 driver 下载失败，要走镜像源或离线包。

### 9. 测试数据依赖
- 用例依赖前置数据存在 → 环境一重置全挂；
- 原则：**造数走接口、验证走 UI**；用例数据自造自销；唯一性数据加时间戳后缀。

### 10. 并行执行
- WebDriver **不是线程安全**的，一个 driver 不能多线程共享；
- pytest-xdist 按用例进程级并行，每个 worker 独立 driver；
- 并行跑同一账号会互相挤掉登录态，用账号池/数据隔离。

### 11. 浏览器进程残留 / 内存泄漏
- `close()` 只关当前窗口，`quit()` 才销毁 driver 进程——用例结束必须 quit，否则 CI 跑几轮内存爆掉、chromedriver 进程成堆；
- 用 fixture `yield driver; driver.quit()` 保证异常时也能回收。

### 12. 用例执行慢的优化
- 消灭固定 sleep；登录态复用（cookie）跳过重复登录；前置数据走接口；pageLoadStrategy 调 eager；非必要用例转接口层。

### 13. 「定位不到元素」通用排查清单
按顺序查：
1. 是不是在 iframe / frame 里？
2. 是不是在 Shadow DOM 里？
3. 是不是在新窗口/新 tab 里？
4. 页面/元素加载完了吗（加显式等待）？
5. 定位表达式在 DevTools Console 里 `$x()` / `$$()` 验证过吗？
6. 元素是否动态 ID/class，表达式失效了？
7. 页面有没有报错中断渲染（看 console 日志）？

### 14. 可观测性建设（团队级）
- 每步操作打日志、失败截图、录屏（docker-selenium 自带）、console 日志收集（Selenium 4 BiDi / `get_log('browser')`）；
- 报告用 Allure 承载，截图/日志挂附件，否则线上环境失败根本没法查。

---

## 六、数据加密类问题（金融/政务项目高频）

### 1. 传输字段加密，页面与报文不一致
- **现象**：`input.get_attribute('value')` 拿到的是明文，但抓包看到的请求体是一串密文；断言"输入框内容等于提交内容"失败。
- **原因**：登录密码、证件号等敏感字段由前端公钥加密后再提交（RSA/SM2），DOM 里保留的是用户键入值。
- **解决**：
  - 断言口径二选一：要么校验**页面上"实际请求报文"区域**，要么用 CDP / selenium-wire 抓真实请求体；
  - 公钥多为异步接口下发 → 提交前必须等密钥就绪（`WebDriverWait` 到指纹/READY 出现），不能一进页面就点；
  - 加了随机填充的算法（RSA-OAEP、SM2）**同一明文每次密文都不同**，禁止对密文做字符串相等断言，应断言服务端回显或结构化字段；
  - 密钥轮换后旧密文必然失败，脚本里不要跨用例缓存密文。

### 2. 页面脱敏，断言拿不到真实值
- **现象**：页面手机号显示 `138****8000`、余额显示 `¥ ****.**`，断言完整号码失败；少数行 DOM 上有 `data-raw` 明文，大多数没有。
- **原因**：合规要求最小可见原则，完整值由独立的"查看/解密"接口提供，且常带审计与冷却。
- **解决**：
  - 基准数据取服务端接口（如全量明文接口/导出），不要以页面文本为准；
  - `data-raw` 一类的属性值属泄漏，可能只覆盖个别行，只可做辅助手段；
  - 明文抽屉/浮层常**限时自动收起**，打开后立刻取值，中间不要插入 sleep；
  - 同一条记录有查看冷却，批量核对需换记录或等待；
  - 区分「未登记（—）」与「金额为 0」，两者断言不能混写。

### 3. 密文存储，页面数字与库表无法直连比对
- **现象**：页面显示正常明文，直连 DB 看到一片 base64 密文；同一条数据两次写入密文不同；部分行解密失败。
- **原因**：敏感字段以对称加密（AES-GCM 等）落库，IV 随机导致密文不确定；存在历史密钥版本与已吊销密钥。
- **解决**：
  - 必须先**按行记录的密钥版本**解密后再比对，不能拿密文做等值/求和处理；
  - 需要密文字段检索时用摘要列（HMAC/SHA256）而非密文本身；
  - 分页/汇总字段漂移问题叠加：务必取全量行（参见本文件"读数一致性"相关条目）；
  - 三种行状态要分别断言：解密成功 / 解密失败（密钥问题）/ 未登记（NULL）；
  - 测试环境密钥常随实例生成，跨会话缓存的密文必然失效，用例开始先重新取数。

### 4. 接口报文整体加密 + 时间戳/签名
- **现象**：直接 `requests` 调接口返回的 JSON 里只有 `enc/iv/ts/sign`，没有业务字段；隔几分钟复用旧报文报"签名过期"。
- **原因**：响应体整体加密（或加签），客户端 SDK 负责解密与验签；签名通常绑定时间戳窗口防重放。
- **解决**：
  - 接口层用例要补齐链路：取会话密钥 → 解密 → 断言业务字段 → 校验签名；
  - 注意"解密成功"不等于"验签通过"（篡改模式往往只动签名不动密文），两个断言分开做；
  - 时间戳窗口一般几十到几百秒，取到报文后尽快校验，不要缓存；
  - UI 层则以页面解密后的 DOM/操作结果日志为锚点，失败提示多用浮层且自动消失，不能抓浮层做断言。

---

## 附：优先级建议（排障投入产出比）

| 优先级 | 事项 |
|---|---|
| P0 | 显式等待体系 + 失败截图 + driver 回收（quit），这三件解决 70% 的不稳定 |
| P1 | 元素定位规范（data-testid 推动）、iframe/新窗口切换封装成工具方法 |
| P2 | CI 环境固化（浏览器版本、分辨率、字体、时区）、兼容性矩阵按客户环境裁剪 |
| P3 | 分布式并行、录屏、Bot 检测对抗等进阶项 |
