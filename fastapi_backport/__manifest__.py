# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fastapi Backport",
    "summary": "Backport of FastAPI to Odoo 14.0",
    "version": "14.0.1.0.0",
    "author": " Akretion",
    "license": "AGPL-3",
    "depends": [
        "sixteen_in_fourteen",
        "base_contextvars",
        "base_future_response",
        "fastapi",
        "pydantic",
        "extendable_fastapi",
        "extendable",
    ],
    "post_init_hook": "post_init_hook",
}
