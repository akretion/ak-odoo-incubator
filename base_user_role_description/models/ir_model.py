# Copyright 2025 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

from odoo import fields, models

MAPPING_KIND_MODELS = {
    "Article": [
        "product.product",
        "product.template",
        "product.categorie",
        "product.attribute",
        "product.attribute.value",
        "uom.uom",
        "hs.code",
        "product.packaging.type",
        "product.packaging",
    ],
    "Vente": [
        "sale.order",
        "product.pricelist",
        "product.pricelist.item",
        "crm.team",
        "delivery.carrier",
    ],
    "Achat": [
        "purchase.order",
        "product.supplierinfo",
    ],
    "Logistique": [
        "stock.picking",
        "stock.move",
        "stock.move.line",
        "stock.picking.type",
        "stock.quant",
        "stock.location",
        "stock.warehouse",
        "stock.lot",
        "stock.route",
        "stock.warehouse.orderpoint",
        "stock.putaway.rule",
        "stock.inventory",
        "stock.inventory.line",
    ],
    "Production": [
        "mrp.bom",
        "mrp.production",
        "mrp.workorder",
    ],
    "Comptabilité": [
        "account.account",
        "account.tax",
        "account.journal",
        "account.product.fiscal.classification",
        "account.fiscal.position",
    ],
    "Immobilisation": [
        "account.asset",
        "account.asset.profile",
        "account.asset.category",
    ],
    "Facturation": [
        "account.move",
        "account.payment",
        "account.account.type",
        "account.payment.term",
        "account.incoterms",
    ],
    "Banque": [
        "account.reconcile.model",
        "account.bank.statement",
        "res.partner.bank",
        "res.bank",
        "online.bank.statement.provider",
    ],
    "Projet": [
        "project.project",
        "project.task",
    ],
    "Contact": [
        "res.partner",
        "res.country",
        "res.company",
    ],
    "Calendrier": [
        "calendar.event",
        "resource.calendar",
    ],
    "Support": [
        "helpdesk.ticket",
    ],
    "Utilisateur": [
        "res.users",
    ],
    "Sécurité": [
        "ir.model.access",
        "ir.rule",
        "res.groups",
        "res.users.role",
    ],
    "CRM": [
        "crm.lead",
        "crm.stage",
    ],
    "Employé": [
        "hr.employee",
        "hr.contract",
        "hr.leave",
    ],
    "Point de vente": [
        "pos.order",
        "pos.session",
        "pos.config",
    ],
    "File d'attente des travaux": [
        "queue.job",
        "attachment.queue",
        "queue.job.channel",
    ],
    "Technique": [
        "ir.module.module",
    ],
    "documents": [
        "dms.file",
        "dms.directory",
    ],
    "Maintenance": [
        "maintenance.equipment",
        "maintenance.equipment.network",
        "maintenance.team",
    ],
}


class IrModel(models.Model):
    _inherit = "ir.model"

    model_for_role_descr = fields.Boolean(
        string="Model for Role Description",
        compute="_compute_for_role_descr",
        store=True,
    )

    def get_mapping_kind_models(self):
        return MAPPING_KIND_MODELS

    def get_kinds_for_role_descr(self):
        return [
            (kind, kind.capitalize()) for kind in self.get_mapping_kind_models().keys()
        ] + [("other", "Other")]

    kind_for_role_descr = fields.Selection(
        selection=get_kinds_for_role_descr,
        string="Kind for Role Description",
        compute="_compute_for_role_descr",
        store=True,
    )

    def _compute_for_role_descr(self):
        mapping = self.get_mapping_kind_models()
        for rec in self:
            rec.kind_for_role_descr = "other"
            for kind, models in mapping.items():
                if rec.model in models:
                    rec.kind_for_role_descr = kind
                    rec.model_for_role_descr = True
                    break

    def _cron_update_model_for_role_descr(self):
        self.search([])._compute_for_role_descr()
