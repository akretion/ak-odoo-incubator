import marimo

import polars as pl

import odoo.http as http
from odoo.http import Controller, request
from odoo.modules.module import get_module_path

ROUTE = "/marimo/<string:model>"


class Marimo(Controller):
    @http.route(
        [ROUTE],
        type="http",
        auth="user",
    )
    def _get_model(self, model):
        # data = request.env[model].search([], limit=100)
        data = request.env["res.users"].search([], limit=100)
        df = pl.from_dicts(data.read(['name', 'login']))
        print(df)
        # to be continued ...
        return df.__repr__()


# http://myproject.localhost/marimo/res.users

# https://github.com/marimo-team/marimo
# https://docs.marimo.io/guides/working_with_data/dataframes/#transforming-dataframes
# https://docs.marimo.io/guides/working_with_data/dataframes/#dataframe-panels
# https://docs.marimo.io/guides/working_with_data/plotting/#chart-builder
# https://docs.marimo.io/api/plotting/#other-plotting-libraries
# https://docs.marimo.io/examples/

# https://github.com/Energie-De-Nantes/electricore/blob/main/electricore/core/loaders/odoo/reader.py#L18

# https://github.com/CodeCutTech/marimo-dashboard-demo/blob/main/dashboard.py
