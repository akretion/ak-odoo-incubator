from odoo.tests.common import TransactionCase


class Test(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)

    def test_no_missing_data_in_default_code(self):
        data_list = ["E-COM07", "FURN_7777", "FURN_6666"]
        unknown_data = self.unknown_data_in_default_code(data_list)
        assert not unknown_data

    def test_missing_data_in_default_code(self):
        data_list = ["FURN_7777", "ANY", "E-COM07", "E-COM08", "MISS-TEAK"]
        unknown_data = self.unknown_data_in_default_code(data_list)
        assert unknown_data == ["ANY", "MISS-TEAK"]

    def test_missing_data_in_default_code_with_company(self):
        data_list = ["FURN_7777", "ANY", "MISS-TEAK"]
        self.env["product.product"].create(
            {"default_code": "ANY", "name": "ANY", "company_id": 1}
        )
        unknown_data = self.env["base"]._unknown_data_in_field(
            "product.product", "default_code", data_list, company_id=1
        )
        assert unknown_data == ["FURN_7777", "MISS-TEAK"]

    def unknown_data_in_default_code(self, data_list):
        return self.env["base"]._unknown_data_in_field(
            "product.product", "default_code", data_list
        )
