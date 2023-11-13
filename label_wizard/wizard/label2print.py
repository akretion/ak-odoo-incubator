# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError

# Attention: gros refactoring a prévoir
# on veux imprimer des étiquettes produits avec
# la bonne quantité (picking, stock move line)
# ou les N° de lots (stock move line, quants)
# Il faut prévoir un refactoring: ne plus utiliser
# le format textuel, mais une tree view
# ça économisera les parsing


class LabelFromRecord(models.TransientModel):
    _name = "label.from.record"
    _inherit = ["proxy.action.helper"]
    _description = "Print products label"

    @api.model
    def __get_label_content(self):
        return self._get_label_content()

    content = fields.Text(string="Label's content", default=__get_label_content)
    with_price = fields.Boolean(string="Print price", help="Print price on labels")

    @api.model
    def _get_label_content(self):
        infos = []
        model = self._context["active_model"]
        if model == "stock.picking":
            # PICKING
            if self._context.get("active_id"):
                moves = self.env["stock.move"].search(
                    [("picking_id", "=", self._context["active_id"])]
                )
                infos = [
                    "%s ; %s ; %s"
                    % (
                        x.product_id.default_code or "_",
                        int(x.product_uom_qty),
                        x.product_id.id,
                    )
                    for x in moves
                    if x.product_id
                ]
        elif model in ("product.product", "product.template"):
            # PRODUCT
            products = self.env[model].browse(self._context["active_ids"])
            infos = [
                "{} ; {} ; {}".format(x.default_code or "_", 1, x.id) for x in products
            ]
        elif model in ("stock.quant", "stock.move.line"):
            # quant
            def find_qty(x):
                if model == "stock.move.line":
                    return int(x.qty_done)
                else:
                    return 1

            records = self.env[model].browse(self._context["active_ids"])
            infos = [
                "%s ; %s ; %s ; %s"
                % (
                    x.product_id.default_code or "_",
                    find_qty(x),
                    x.product_id.id,
                    x.id,
                )
                for x in records
                if x.product_id
            ]
        return "\n".join(infos)

    def generate_label(self):
        printer_host = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("label_printer_poc.printer_host")
        ) or "https://localhost:443"
        printer_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("label_printer_poc.product_label_printer_name")
        ) or "zebra_large"
        for rec in self:
            if rec.content:
                printed_product_list = []
                print_data = []
                lines = rec.content.split("\n")
                for line in lines:
                    # on remplace le text par des entiers quand possible
                    # 0 est considéré comme False donc n'est pas
                    # transformé en entier
                    parts = [
                        (x.strip().isdigit() and int(x.strip()) or x.strip())
                        for x in line.split(";")
                        if x.strip()
                    ]
                    rec._sanitize_and_check_parts(parts, line)
                    printed_product_list.append(parts[:])

                for info in printed_product_list:
                    product, quantity = rec._search_product(info)
                    if product:
                        print_data.append((product, quantity))

                if len(print_data) > 0:
                    model = print_data[0][0].browse(False)
                    zebra_print_data = model.get_labels_zebra(
                        print_data, with_price=rec.with_price
                    )
                    action_list = [
                        self.get_print_data_action(
                            data,
                            copies=quantity,
                            printer_name=printer_name,
                            raw=True,
                            host=printer_host,
                        )
                        for data, quantity in zebra_print_data
                    ]
                    return self.send_proxy(action_list)

        return {"type": "ir.actions.act_window_close"}

    @api.model
    def _search_product(self, info):
        """info[0]: code,
        info[1]: quantity,
        info[2]: id product,
        info[3]: id move_line or quant
        return record, quantity
        """
        qty = info[1]
        if len(info) == 4:
            model = self._context["active_model"]
        else:
            model = "product.product"
        if len(info) > 2:
            # the last part is always the id
            rec = self.env[model].browse(info[-1])
            if rec:
                return (rec, qty)
        products = model.search([("default_code", "=", info[0])])
        if products:
            return (products[0], qty)
        return (False, False)

    @api.model
    def _sanitize_and_check_parts(self, parts, line):
        """@return la 1ère règle non respecté"""
        message = "La ligne '%s' ne respecte pas le format."
        if not isinstance(parts, list):
            raise UserError(_(message) % line)
        if len(parts) <= 2:
            raise UserError(_(message) % line)
        if len(parts) >= 5:
            raise UserError(_("Plus de 4 segments. " + message) % line)
        if not isinstance(parts[1], int):
            raise UserError(_("La quantité n'est pas un entier '%s'") % line)
        if parts[1] <= 0:
            raise UserError(_("La quantité ne peut être <= 0. '%s'") % line)
        if len(parts) > 2 and not isinstance(parts[2], int):
            raise UserError(_("L'id n'est pas un entier '%s'") % line)
        return True
