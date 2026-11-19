# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessDenied
from odoo.http import Controller, request, root, route

from odoo.addons.web.controllers.utils import _get_login_redirect_url


class DatabaseInstanceController(Controller):
    @route(
        ["/web/instance/<int:user_id>/<string:token>/connect"],
        methods=["GET"],
        type="http",
        auth="public",
    )
    def db_instance_connect(
        self,
        user_id,
        token,
        **params,
    ):
        user = request.env["res.users"].sudo().browse(user_id)
        if not user:
            # Do not leak information about existing users
            raise AccessDenied()

        user._check_instance_db_token(token)

        user = user.with_user(user)
        user._update_last_login()
        env = request.env(user=user.id)

        # Create a odoo session
        request.session.uid = user.id
        request.session.login = user.login
        request.session.context = dict(env["res.users"].context_get())
        request.session.session_token = user._compute_session_token(request.session.sid)
        request.env.registry.clear_cache()
        root.session_store.rotate(request.session, env)
        return request.redirect(_get_login_redirect_url(user.id))
