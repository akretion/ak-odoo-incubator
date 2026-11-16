# Copyright 2026 Akretion France (https://www.akretion.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

DEFAULTS = {
    "allianz_trade.idp_base_uat": (
        "https://api-services.uat.1placedessaisons.com/uatm/v1/idp"
    ),
    "allianz_trade.idp_base_prod": "https://api.allianz-trade.com/v1/idp",
    "allianz_trade.gradecheck_base_uat": (
        "https://api-services.uat.1placedessaisons.com/uatm/grade-check/v1"
    ),
    "allianz_trade.gradecheck_base_prod": "https://api.allianz-trade.com/grade-check/v1",
}


def post_init_hook(env):
    icp = env["ir.config_parameter"].sudo()
    for key, value in DEFAULTS.items():
        # keep values of an existing setup
        if not icp.get_str(key):
            icp.set_str(key, value)
