from odoo import api, fields, models

CONFIG_ELEMENTS = ["width", "depth", "screw", "support", "finish", "joinery"]


class SupportType(models.Model):
    _name = "demo.mrp.config.support.type"
    _description = "demo.mrp.config.support.type"

    name = fields.Char()
    value = fields.Char()


class ScrewType(models.Model):
    _name = "demo.mrp.config.screw.type"
    _description = "demo.mrp.config.screw.type"

    name = fields.Char()
    value = fields.Char()


class ShelfSupportScrewConstraint(models.Model):
    _name = "demo.shelf.screw.support"
    _description = "demo.shelf.screw.support"

    shelf = fields.Many2one(comodel_name="product.template")
    support = fields.Many2one(comodel_name="demo.mrp.config.support.type")
    screw = fields.Many2many(comodel_name="demo.mrp.config.screw.type")


class InputLine(models.Model):
    _name = "input.line"
    _inherit = "input.line"

    width = fields.Float()
    depth = fields.Float()
    area = fields.Float(compute="_compute_area")

    support = fields.Many2one(comodel_name="demo.mrp.config.support.type", store=True)
    support_domain = fields.Binary(compute="_compute_support_domain")

    screw = fields.Many2one(comodel_name="demo.mrp.config.screw.type", store=True)
    screw_domain = fields.Binary(compute="_compute_screw_domain")

    finish = fields.Many2one(comodel_name="product.product")
    should_show_finish = fields.Boolean(
        compute="_compute_should_show_finish", store=True
    )

    joinery = fields.Many2one(comodel_name="product.template")
    should_show_joinery = fields.Boolean(
        compute="_compute_should_show_joinery", store=True
    )

    @api.depends("width", "depth")
    def _compute_area(self):
        for rec in self:
            rec.area = rec.width / 1000 * rec.depth / 1000

    @api.depends("bom_id")
    def _compute_support_domain(self):
        for rec in self:
            constraints = self.env["demo.shelf.screw.support"].search(
                [("shelf.id", "=", self.bom_id.product_tmpl_id.id)]
            )
            available_support_ids = constraints.support.mapped("id")
            rec.support_domain = [("id", "=", available_support_ids)]

            if rec.support.id not in available_support_ids:
                rec.support = False

    @api.depends("support")
    def _compute_screw_domain(self):
        for rec in self:
            constraints = self.env["demo.shelf.screw.support"].search(
                [
                    ("shelf.id", "=", self.bom_id.product_tmpl_id.id),
                    ("support.id", "=", self.support.id),
                ]
            )
            available_screw_ids = constraints.screw.mapped("id")
            rec.screw_domain = [("id", "=", available_screw_ids)]

            if rec.screw.id not in available_screw_ids:
                rec.screw = False

    @api.depends("bom_id")
    def _compute_should_show_finish(self):
        for rec in self:
            rec.should_show_finish = rec.bom_id.product_tmpl_id == self.env.ref(
                "mrp_bom_configurable_demo.demo_mrp_bom_configurable_shelf_wood"
            )

    @api.depends("width")
    def _compute_should_show_joinery(self):
        for rec in self:
            rec.should_show_joinery = (
                rec.width >= 1000
                and rec.bom_id.product_tmpl_id
                == self.env.ref(
                    "mrp_bom_configurable_demo.demo_mrp_bom_configurable_shelf_wood"
                )
            )

    def _get_config_elements(self):
        return CONFIG_ELEMENTS

    def populate_bom_data_preview(self):
        self.ensure_one()
        bom = self.bom_id
        content = bom.get_bom_configured_data(self)
        self.env["mrp.bom"].create(
            {
                "product_tmpl_id": bom.product_tmpl_id.id,
                "product_id": bom.product_id.id,
                "product_qty": 1,
                "product_uom_id": bom.product_uom_id.id,
                "configuration_type": "configured",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": line["product_id"].id,
                            "product_qty": line["product_qty"],
                            "product_uom_id": line["product_uom_id"].id,
                        },
                    )
                    for line in content
                ],
            }
        )


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = "sale.order.line"

    @api.depends(
        "input_line_id.bom_id",
        "input_line_id.width",
        "input_line_id.depth",
        "input_line_id.screw",
        "input_line_id.support",
        "input_line_id.finish",
        "input_line_id.joinery",
    )
    def _compute_should_compute_price(self):
        for rec in self:
            if not rec.is_static_product:
                rec.should_compute_price = True
