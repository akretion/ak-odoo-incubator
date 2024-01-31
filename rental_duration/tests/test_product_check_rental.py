# Copyright 2024 Groupe Voltaire
# @author Emilie SOUTIRAS <emilie.soutiras@groupevoltaire.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase
from odoo import _



class TestSaleRentalVariant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.rented_template = cls.env.ref("product.product_product_4_product_template")
        cls.rented_product = cls.rented_template.product_variant_ids[0]
        cls.day_uom_id = cls.env.ref("uom.product_uom_day").id
        cls.rental_product = cls.env["product.product"].create(
            {
                "name": "Rent service",
                "type": "service",
                "rented_product_id": cls.rented_product.id,
                "sale_ok": True,
                "purchase_ok": False,
                "uom_id": cls.day_uom_id,
                "uom_po_id": cls.day_uom_id,
                "must_have_dates": True,
                "invoice_policy": "order",
            }
        )
        cls.rental_template = cls.rental_product.product_tmpl_id

    def test_check_rental_rented_fields(self):
        self.assertEqual(self.rental_template.must_have_duration, False)
        self.assertEqual(self.rental_product.must_have_duration, False)

    def test_check_rental_update_type(self):
        self.rental_product.must_have_duration = True
        with self.assertRaises(
                ValidationError,
                msg=_("The rental product '%s' must be of type 'Service'.")
                    % self.rental_product.name
        ):
            self.rental_product.write({
                'type': "consu",
                'must_have_duration': True
            })

    def test_check_rental_update_must_have_dates(self):
        with self.assertRaises(
                ValidationError,
                msg=_("The rental product '%s' must have the option "
                      "'Must Have Start and End Dates' checked.")
                    % self.rental_product.name
        ):
            self.rental_product.write({
                'must_have_dates': False,
                'must_have_duration': True
            })

    def test_check_rental_update_uom_id(self):
        self.rental_product.must_have_duration = True
        self.rental_product.uom_id = self.env.ref("rental_duration.product_uom_month").id
        self.assertNotEqual(self.rental_product.uom_id.id, self.day_uom_id)

    def test_update_rented_pdt_with_wrong_type(self):
        product = self.env.ref("product.product_product_3")
        rental_product = self.create_product(
            with_duration=False,
            other_vals={"type": "consu"})
        with self.assertRaises(
                ValidationError,
                msg=_("The rental product '%s' must be of type 'Service'.")
                    % rental_product.name
        ):
            rental_product.write({
                'rented_product_id': product.id,
                'must_have_duration': True
            })

    def test_super_update_rented_pdt_with_wrong_type(self):
        """ test super._check_rental is called and raise error """
        product = self.env.ref("product.product_product_3")
        rental_product = self.create_product(
            with_duration=False,
            other_vals={"type": "consu"})
        with self.assertRaises(
                ValidationError,
                msg=_("The rental product '%s' must be of type 'Service'.")
                    % rental_product.name
        ):
            rental_product.write({
                'rented_product_id': product.id,
            })

    def test_update_rented_pdt_with_wrong_must_have_dates(self):
        product = self.env.ref("product.product_product_3")
        rental_product = self.create_product(
            with_duration=False,
            other_vals={'must_have_dates': False})
        with self.assertRaises(
                ValidationError,
                msg=_("The rental product '%s' must have the option "
                            "'Must Have Start and End Dates' checked.")
                    % rental_product.name
        ):
            rental_product.write({
                'rented_product_id': product.id,
                'must_have_duration': True
            })

    def test_super_update_rented_pdt_with_wrong_must_have_dates(self):
        """ test super._check_rental is called and raise error """
        product = self.env.ref("product.product_product_3")
        rental_product = self.create_product(
            with_duration=False,
            other_vals={'must_have_dates': False})
        with self.assertRaises(
                ValidationError,
                msg=_("The rental product '%s' must have the option "
                            "'Must Have Start and End Dates' checked.")
                    % rental_product.name
        ):
            rental_product.write({
                'rented_product_id': product.id,
            })

    def test_update_rented_pdt_with_wrong_uom_id(self):
        product = self.env.ref("product.product_product_3")
        rental_product = self.create_product(
            with_duration=True,
            other_vals={
             "uom_id": self.env.ref("rental_duration.product_uom_month").id,
             "uom_po_id": self.env.ref("rental_duration.product_uom_month").id,
        })
        rental_product.write({
            'rented_product_id': product.id,
            'must_have_duration': True
        })
        self.assertNotEqual(rental_product.uom_id.id, self.day_uom_id)

    def test_super_update_rented_pdt_with_wrong_uom_id(self):
        """ test super._check_rental is called and raise error """
        product = self.env.ref("product.product_product_3")
        rental_product = self.create_product(
            with_duration=True,
            other_vals={
             "uom_id": self.env.ref("rental_duration.product_uom_month").id,
             "uom_po_id": self.env.ref("rental_duration.product_uom_month").id,
        })
        with self.assertRaises(
                ValidationError,
                msg=_("The unit of measure of the rental product '%s'  must be 'Day'.")
                    % rental_product.name
        ):
            rental_product.write({
                'rented_product_id': product.id,
                'must_have_duration': False
            })

    def create_product(self, with_duration=True, other_vals=None):
        vals = self.get_vals()
        if not with_duration:
            vals.update({'must_have_duration': False})
        if other_vals:
            vals.update(other_vals)
        rental_product = self.env["product.product"].create(vals)
        return rental_product

    def get_vals(self):
        return {
            "name": "Rent service test",
            "type": "service",
            "sale_ok": True,
            "purchase_ok": False,
            "rented_product_id": False,
            "uom_id": self.day_uom_id,
            "uom_po_id": self.day_uom_id,
            "must_have_dates": True,
            "must_have_duration": True,
            "invoice_policy": "order",
        }

    def test_creation_type_with_rented(self):
        product = self.env.ref("product.product_product_3")
        vals = self.get_vals()
        vals.update({
            "type": "consu",
            "rented_product_id": product.id
        })
        with self.assertRaises(
                ValidationError,
                msg=_("The rental product '%s' must be of type 'Service'.")
                    % vals['name']
        ):
            self.env["product.product"].create(vals)

    def test_creation_must_have_dates_with_rented(self):
        product = self.env.ref("product.product_product_3")
        vals = self.get_vals()
        vals.update({
            "must_have_dates": False,
            "rented_product_id": product.id
        })
        with self.assertRaises(
                ValidationError,
                msg=_("The rental product '%s' must have the option "
                            "'Must Have Start and End Dates' checked.")
                    % vals['name']
        ):
            self.env["product.product"].create(vals)

    def test_creation_uom_id_with_rented(self):
        product = self.env.ref("product.product_product_3")
        vals = self.get_vals()
        vals.update({
            "uom_id": self.env.ref("rental_duration.product_uom_month").id,
            "uom_po_id": self.env.ref("rental_duration.product_uom_month").id,
            "rented_product_id": product.id
        })
        rental_pdt = self.env["product.product"].create(vals)
        self.assertNotEqual(rental_pdt.uom_id.id, self.day_uom_id)
