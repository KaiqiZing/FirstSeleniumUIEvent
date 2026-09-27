# -*- coding: utf-8 -*-
"""Flask 入口：注册 CORS 与各业务蓝图。运行：cd backend && python app.py"""
from flask import Flask
from flask_cors import CORS

import db
import vault_db
from config import Config
from api import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)

    # 初始化 SQLite：建库建表，首次启动灌入初始数据
    db.init_db()
    vault_db.init_vault()

    register_blueprints(app)

    @app.get("/api/health")
    def health():
        return {"code": 0, "data": {"status": "up"}, "message": "ok"}

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=Config.PORT, debug=False, threaded=True)
