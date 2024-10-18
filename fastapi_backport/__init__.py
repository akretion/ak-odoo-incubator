# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from . import models
from . import http
from starlette.responses import JSONResponse
from odoo import SUPERUSER_ID, api
from odoo.addons.extendable.models.ir_http import IrHttp
from odoo.addons.fastapi.fastapi_dispatcher import FastApiDispatcher
from odoo.addons.fastapi.tests.common import FastAPITransactionCase
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


# Use SavepointCase instead of TransactionCase (16.0 merge)
# And use test mode to avoid deadlock in envioronment RLock
class TestModeSavepointCase(SavepointCase):
    def setUp(self):
        super().setUp()
        self.registry.enter_test_mode(self.env.cr)

    def tearDown(self):
        self.registry.leave_test_mode()
        super().tearDown()

    @classmethod
    def _patch_app_to_handle_exception(cls, app):
        def handle_error(request, exc):

            def make_json_response(body, status, headers):
                response = JSONResponse(body, status_code=status)
                if status == 500:
                    _logger.error("Error in test request", exc_info=exc)
                if headers:
                    response.headers.update(headers)
                return response

            request.make_json_response = make_json_response
            return FastApiDispatcher(request).handle_error(exc)

        app.exception_handlers = {Exception: handle_error}


FastAPITransactionCase.__bases__ = (TestModeSavepointCase,)


@classmethod
def _dispatch(cls):
    with cls._extendable_context_registry():
        return super(IrHttp, cls)._dispatch()


IrHttp._dispatch = _dispatch


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # this is the trigger that sends notifications when jobs change
    _logger.info("Resyncing registries")
    endpoints_ids = env["fastapi.endpoint"].search([]).ids
    env["fastapi.endpoint"]._handle_registry_sync(endpoints_ids)
