#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo.tests import common


class MulticompanySubmitCase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(MulticompanySubmitCase, cls).setUpClass()
        # active multicompany
        cls.env.ref("product.product_comp_rule").active = True

        cls.company_approver = cls.env.ref(
            "product_multicompany_submit.demo_company_approver"
        )
        cls.company_submitter = cls.env.ref(
            "product_multicompany_submit.demo_company_submitter"
        )
        cls.company_other = cls.env.ref(
            "product_multicompany_submit.demo_company_other"
        )
        cls.user_approver = cls.env.ref(
            "product_multicompany_submit.demo_user_approver"
        )
        cls.user_submitter = cls.env.ref(
            "product_multicompany_submit.demo_user_submitter"
        )
        cls.user_other = cls.env.ref("product_multicompany_submit.demo_user_other")
        cls.product = cls.env.ref("product_multicompany_submit.demo_product_submit")

        cls.product.button_multicompany_submit()
