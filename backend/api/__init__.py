# -*- coding: utf-8 -*-


def register_blueprints(app):
    from . import (
        auth_api,
        captcha_api,
        crypto_api,
        dbconsistency_api,
        export_api,
        settlement_api,
        slow_api,
    )

    for bp in (
        slow_api.bp,
        export_api.bp,
        captcha_api.bp,
        auth_api.bp,
        settlement_api.bp,
        dbconsistency_api.bp,
        crypto_api.bp,
    ):
        app.register_blueprint(bp, url_prefix="/api")
