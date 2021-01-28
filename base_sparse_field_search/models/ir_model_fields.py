from odoo import fields, models


class Base(models.AbstractModel):
    _inherit = "base"

    def _valid_field_parameter(self, field, name):
        return name == "sparse_search" or super()._valid_field_parameter(field, name)


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    sparse_search = fields.Boolean()

    def _instanciate_attrs(self, field_data):
        attrs = super(IrModelFields, self)._instanciate_attrs(field_data)
        if attrs and field_data.get("sparse_search"):
            attrs["sparse_search"] = True
        return attrs

    def _reflect_field_params(self, field, model_id):
        res = super()._reflect_field_params(field, model_id)
        res["sparse_search"] = field.sparse_search
        return res
