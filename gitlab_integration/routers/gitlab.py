# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends, Header

from odoo import api
from odoo.exceptions import AccessDenied

from odoo.addons.fastapi.dependencies import fastapi_endpoint, odoo_env
from odoo.addons.fastapi.models.fastapi_endpoint import FastapiEndpoint

gitlab_router = APIRouter(tags=["gitlab"])


@gitlab_router.post("/webhook")
def gitlab_webhook(
    env: Annotated[api.Environment, Depends(odoo_env)],
    x_gitlab_token: Annotated[str, Header()],
    endpoint: Annotated[FastapiEndpoint, Depends(fastapi_endpoint)],
    payload: dict,
) -> dict:
    if x_gitlab_token != endpoint.gitlab_token:
        raise AccessDenied(env._("Invalid Gitlab token"))
    if payload.get("object_kind") == "merge_request":
        env["gitlab.merge.request"].process_webhook(payload)
    return {"status": "ok"}
