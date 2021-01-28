from openerp import fields, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    sparse_search = fields.Boolean()
