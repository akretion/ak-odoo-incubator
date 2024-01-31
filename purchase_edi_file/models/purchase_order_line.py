#  Copyright (C) 2021 Akretion (http://www.akretion.com).

from odoo import _, exceptions, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_lines_by_profiles(self, partner):
        profile_lines = {
            key: self.env["purchase.order.line"]
            for key in partner.edi_purchase_profile_ids
        }
        for line in self:
            product = line.product_id
            # the goal of finding the supplierinfo is to get the edi profile
            # so we don't need to put the right line quantity, just any supplierinfo
            # for this supplier should be enough. (We avoid error in case purchased
            # qty is forced to less than the min of supplierinfo
            seller = product._select_seller(partner_id=partner, quantity=None)
            purchase_edi = seller.purchase_edi_id
            # Services should not appear in EDI file unless an EDI profile
            # is specifically on the supplier info. This way, we avoid
            # adding transport of potential discount or anything else
            # in the EDI file.
            if product.type == "service" and not purchase_edi:
                continue
            if purchase_edi:
                profile_lines[purchase_edi] |= line
            elif partner.default_purchase_profile_id:
                profile_lines[partner.default_purchase_profile_id] |= line
            else:
                raise exceptions.UserError(
                    _("Some products don't have edi profile configured : %s")
                    % (product.default_code,)
                )
        return profile_lines
