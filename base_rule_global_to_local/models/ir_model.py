# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class IrModel(models.AbstractModel):
    _inherit = "ir.model"

    rules_gtl_ids = fields.Many2many("ir.rule", string="Global to local rules")
    rules_gtl_generated_ids = fields.Many2many(
        "ir.rule", string="Automatically generated rules"
    )

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get("rules_gtl_ids"):
            self.gtl_refresh_record_rules()
        return res

    def __gtl_helper_quadruplet_map(self, acl):
        # format read/write/create/delete to 1's and 0's
        rwcd = ("perm_read", "perm_write", "perm_create", "perm_unlink")
        result = ""
        for permission in rwcd:
            if getattr(acl, permission):
                result += "1"
            else:
                result += "0"
        return result

    def _gtl_helper_rule_write(self, rule, perms, groups):
        rwcd = ("perm_read", "perm_write", "perm_create", "perm_unlink")
        idx = 0
        for permission in rwcd:
            rule.write({permission: True if perms[idx] == "1" else False})
            idx += 1
        rule.write({"groups": groups.ids})

    def _gtl_get_acl_groups(self):
        """Returns a dict with key=permission quadruplet
        (e.g '1000' for readonly) and value=groups that have this quadrulplet"""
        self.ensure_one()
        acls = self.env["ir.model.access"].search([("model_id", "=", self._model_id),])
        groups = {}
        for acl in acls:
            perms = self._gtl_helper_quadruplet_map(acl)
            if groups.get(perms):
                groups[perms] += acl.group_id
            else:
                groups[perms] = acl.group_id
        return groups

    # TODO : What do we do when the global rule is activated or deactivated,
    # for example through settings ?
    def gtl_refresh_record_rules(self):
        """Global to local: simply, a global rule is equivalent to a local rule
        with every group that is affected by an ACL for that model.
        Less simply, we also need to take into account differences in permissions.
        Thus, we create every combination of local rules to achieve the same end result
        as having the global rule. By having local rules only, we gain the option to
        relax permissions by adding more local rules."""
        for rec in self:
            rec.rules_gtl_generated_ids.unlink()
            for rule in rec.rules_global_to_local_ids:
                permission_group_map = rec._gtl_get_acl_groups()
                for permission_quadruplet, groups in permission_group_map.items():
                    new_name = (
                        "[Technical] Automatically generated: global to local for rule %s"
                        % rule.name
                    )
                    new_rule = rule.copy({"name": new_name})
                    rec._gtl_helper_quadruplet_write(
                        new_rule, permission_quadruplet, groups
                    )
                    rec.rules_gtl_generated_ids += new_rule
                rule.active = False
