# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

from odoo import fields, models


class ResUsersRoleDescription(models.AbstractModel):
    _name = "res.users.role.description"
    _description = "Abstract model to compute descriptions for user/roles"

    _ir_model_access_field = "recursive_model_access_ids"

    relevant_model_access_ids = fields.Many2many(
        comodel_name="ir.model.access",
        string="Relevant Model Accesses",
        compute="_compute_relevant_model_access_ids",
    )

    menu_description = fields.Html(
        string="Menu Description",
        compute="_compute_menu_description",
        sanitize=False,
        translate=True,
    )

    model_access_description = fields.Html(
        string="Model Access Description",
        compute="_compute_model_access_description",
        sanitize=False,
        translate=True,
    )

    def _get_all_implied_groups(self):
        raise NotImplementedError()

    def _get_relevant_models(self):
        return self.env["ir.model"].search([("model_for_role_descr", "=", True)])

    def _compute_relevant_model_access_ids(self):
        models = self._get_relevant_models()
        access_priority = {
            "no_access": 0,
            "read": 1,
            "write": 2,
            "create": 3,
            "full": 4,
        }
        for rec in self:
            access_ids = []
            for model in models:
                accesses = self.env["ir.model.access"].search(
                    [
                        ("model_id", "=", model.id),
                        ("id", "in", rec.recursive_model_access_ids.ids),
                    ]
                )
                if accesses:
                    most_permissive_access = max(
                        accesses, key=lambda a: access_priority.get(a.access_type, 0)
                    )
                    access_ids.append(most_permissive_access.id)
            rec.relevant_model_access_ids = [(6, 0, access_ids)]

    def _compute_model_access_description(self):
        ok = "✅"
        ko = "❌"

        all_models = self.env["ir.model"].search([("model_for_role_descr", "=", True)])

        models_by_kind = {}
        for model in all_models:
            kind = model.kind_for_role_descr
            models_by_kind.setdefault(kind, []).append(model)

        mapping = self.env["ir.model"].get_mapping_kind_models()
        models_by_kind = dict(
            sorted(
                models_by_kind.items(),
                key=lambda item: (
                    list(mapping.keys()).index(item[0]) if item[0] in mapping else 999
                ),
            )
        )

        for rec in self:
            description = ""
            for kind, models in models_by_kind.items():
                rows = []

                for model in models:
                    access = rec.relevant_model_access_ids.filtered(
                        lambda a: a.model_id == model
                    )
                    if access:
                        access = access[0]
                        row = (
                            f"<tr>"
                            f"<td style='padding:4px;'>{model.name}</td>"
                            f"<td style='text-align:center;padding:4px;'>{ok if access.perm_read else ko}</td>"
                            f"<td style='text-align:center;padding:4px;'>{ok if access.perm_write else ko}</td>"
                            f"<td style='text-align:center;padding:4px;'>{ok if access.perm_create else ko}</td>"
                            f"<td style='text-align:center;padding:4px;'>{ok if access.perm_unlink else ko}</td>"
                            f"</tr>"
                        )
                        rows.append(row)

                if rows:
                    kind_label = dict(
                        self.env["ir.model"].fields_get(["kind_for_role_descr"])[
                            "kind_for_role_descr"
                        ]["selection"]
                    )[kind]

                    description += (
                        f"<h3 style='margin:12px 0 4px 0;"
                        f"font-size:1.2em;color:#2c3e50;"
                        f"text-transform:uppercase;"
                        f"letter-spacing:0.5px;"
                        f"border-bottom:2px solid #2980b9;"
                        f"display:inline-block;'>"
                        f"{kind_label}</h3>"
                    )

                    description += f"""
                    <table style="
                        border-collapse:collapse;
                        width:100%;
                        margin-bottom:24px;
                        font-family:Arial,Helvetica,sans-serif;
                        table-layout:fixed;">
                        <thead>
                            <tr style="background:#ecf0f1;">
                                <th style="width:30%;padding:6px;border:1px solid #bdc3c7;">Modèle</th>
                                <th style="width:17.5%;padding:6px;border:1px solid #bdc3c7;">Lecture</th>
                                <th style="width:17.5%;padding:6px;border:1px solid #bdc3c7;">Modification</th>
                                <th style="width:17.5%;padding:6px;border:1px solid #bdc3c7;">Création</th>
                                <th style="width:17.5%;padding:6px;border:1px solid #bdc3c7;">Suppression</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                    for i, row in enumerate(rows):
                        bg = "#fafafa" if i % 2 == 0 else "#ffffff"
                        description += f'<tr style="background:{bg};">{row[4:]}'
                    description += """
                        </tbody>
                    </table>
                    """
            rec.model_access_description = description

    def _get_relevant_menus(self):
        menus_lvl1 = self.env["ir.ui.menu"].search(
            [
                ("active", "=", True),
                ("parent_id", "=", False),
            ]
        )
        menus_lvl2 = self.env["ir.ui.menu"].search(
            [
                ("active", "=", True),
                ("parent_id", "!=", False),
                ("parent_id.parent_id", "=", False),
            ]
        )
        return (menus_lvl1 + menus_lvl2).sorted(key=lambda m: m.id)

    def _compute_menu_description(self):
        menus = self._get_relevant_menus()
        for rec in self:
            menu_desc = ""

            groups = rec._get_all_implied_groups()

            def _menu_is_visible(menu):
                if not menu.groups_id:
                    return True
                return any(g in groups for g in menu.groups_id)

            lvl1_menus = menus.filtered(
                lambda m: not m.parent_id and _menu_is_visible(m)
            )

            def _render_menu_table(title, menus):
                if not menus:
                    return ""
                html = f"""
               <h3 style='margin:12px 0 4px 0;
                          font-size:1.2em;
                          color:#2c3e50;
                          border-bottom:2px solid #2980b9;
                          display:inline-block;'>{title}</h3>
               <table style="
                   border-collapse:collapse;
                   width:100%;
                   margin-bottom:12px;
                   font-family:Arial,Helvetica,sans-serif;
                   table-layout:fixed;">
                   <thead>
                       <tr style="background:#ecf0f1;">
                           <th style="width:35%;padding:6px;border:1px solid #bdc3c7;">Menu</th>
                           <th style="width:45%;padding:6px;border:1px solid #bdc3c7;">Sous‑menus</th>
                       </tr>
                   </thead>
                   <tbody>
               """
                for i, menu in enumerate(menus):
                    bg = "#fafafa" if i % 2 == 0 else "#ffffff"

                    children = menu.child_id.filtered(
                        lambda c: not c.parent_id.parent_id and _menu_is_visible(c)
                    )
                    children_names = (
                        ", ".join(children.mapped("name")) if children else "–"
                    )

                    html += f"""
                   <tr style="background:{bg};">
                       <td style='padding:4px;'>{menu.name}</td>
                       <td style='padding:4px;'>{children_names}</td>
                   </tr>
                   """
                html += """
                   </tbody>
               </table>
               """
                return html

            menu_desc += _render_menu_table(
                "Menus de niveau1 (et leurs sous‑menus accessibles)", lvl1_menus
            )
            rec.menu_description = menu_desc
