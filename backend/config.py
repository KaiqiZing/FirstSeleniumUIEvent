# -*- coding: utf-8 -*-
"""集中配置：验证码、慢接口、导出任务等模拟参数统一收敛于此。"""
import os


class Config:
    SECRET_KEY = "selenium-ui-demo-secret-change-me"

    # ---- 监听端口 ----
    # macOS 的 5000 常被「隔空播放接收器」占用，默认改 5050；
    # 如需换端口：APP_PORT=6000 python app.py（前端同步设 VITE_API_PORT=6000）
    PORT = int(os.environ.get("APP_PORT", 5050))

    # ---- 验证码 ----
    # 测试环境最佳实践演示：开发侧提供万能验证码开关
    CAPTCHA_UNIVERSAL_ENABLED = True
    CAPTCHA_UNIVERSAL_CODE = "1234"
    CAPTCHA_EXPIRE_SECONDS = 300
    # 验证码字符集（去掉易混淆字符）
    CAPTCHA_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

    # ---- 慢接口 ----
    SLOW_API_DEFAULT_DELAY = 3.0
    SLOW_ROWS = 20

    # ---- 不稳定接口 ----
    UNSTABLE_FAIL_RATE = 0.3
    UNSTABLE_DELAY_RANGE = (0.5, 5.0)

    # ---- 分页造数（懒加载）----
    PAGER_TOTAL = 160
    PAGER_PAGE_SIZE = 10

    # ---- 导出长任务 ----
    EXPORT_STEPS = 20          # 0 -> 100 的步数
    EXPORT_STEP_INTERVAL = 0.5  # 每步间隔（秒）
    EXPORT_ROW_COUNT = 500     # 导出文件行数

    # ---- 加密数据场景 ----
    CRYPTO_PUBKEY_DELAY_RANGE = (0.3, 0.8)  # 公钥签发接口的网络延迟（秒）
    CRYPTO_REVEAL_COOLDOWN = 5              # 同一条记录的明文查看冷却时间（秒）
    CRYPTO_TS_WINDOW = 120                  # 报文时间戳有效窗口（秒）
    CRYPTO_PAGE_SIZE = 5                    # 密文档案分页每页条数
    CRYPTO_ECHO_PLAINTEXT = False           # 练习后门：True 时登录响应才回显明文口令（真实系统严禁）

    # ---- 结算单父子金额 ----
    SETTLEMENT_RECALC_DELAY = 0.8  # 子单金额调整后后台重算耗时（秒）

    # ---- 页面数字 与 数据库 一致性核对（SQLite）----
    DB_PAGE_SIZE = 5              # 明细分页每页条数（共 15 条，需翻页才能取全）
    DB_WRITE_DELAY = 0.6          # 写入后页面异步刷新耗时（秒）
    DB_POST_ACCOUNT = "10000088"  # 「模拟清算入账」默认入账账号
    DB_POST_DELTA_YUAN = 25000.00  # 默认入账金额（元）
