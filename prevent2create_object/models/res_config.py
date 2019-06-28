# coding: utf-8
# © 2018 Akretion Mourad EL HADJ MIMOUNE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.modules.registry import Registry

import logging

logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    forbidden_models = fields.Char(
        default='sale.order,purchase.order,stock.picking,stock.move,'
        'account.invoice,account.move, account.move.line')
    forbidden_models_msg = fields.Char(
        default="Can not create this object on"
        "production data base.\nUse the "
        "preproduction database instead.")


class BaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    forbidden_models = fields.Char(
        related='company_id.forbidden_models',
        help="Modes which can't create because base"
        " is not yet in production. ex sale.order, purchase.order, ...")
    forbidden_models_msg = fields.Char(
        related='company_id.forbidden_models_msg')

    CRITICAL_FIELDS = ['forbidden_models', 'active']

    def _update_registry(self):
        """ Update the registry after a modification
            on base config settings.
        """
        if self.env.registry.ready and not self.env.context.get('import_file'):
            # for the sake of simplicity, simply force the registry to reload
            self._cr.commit()
            self.env.reset()
            registry = Registry.new(self._cr.dbname)
            registry.signal_registry_change()

    @api.model
    def create(self, vals):
        res = super(BaseConfigSettings, self).create(vals)
        if set(vals).intersection(self.CRITICAL_FIELDS):
            self._update_registry()
        return res

    @api.multi
    def write(self, vals):
        res = super(BaseConfigSettings, self).write(vals)
        if set(vals).intersection(self.CRITICAL_FIELDS):
            self._update_registry()
        return res

    @api.model_cr
    def _register_hook(self):
        """ Patch models that should trigger action rules based on creation,
            modification of records and form onchanges.
        """
        def make_create():
            """ Instanciate a create method that processes action rules. """
            @api.model
            def create(self, vals, **kw):
                # restict create method
                forbidden_models = self.env.user.company_id.forbidden_models
                fbd_models_name = forbidden_models and \
                    map(str.strip, str(forbidden_models).split(',')) or []
                if fbd_models_name and self._name in fbd_models_name:
                    defult_msg = (
                        "Can not create this object on"
                        "production data base.\nUse the "
                        "preproduction database instead.")
                    msg = self.env.user.company_id.forbidden_models_msg or\
                        defult_msg
                    raise UserError(msg)

                # call original method
                record = create.origin(self.env, vals, **kw)
                return record
            return create

        patched_models = defaultdict(set)

        def patch(model, name, method):
            """ Patch method `name` on `model`,
             unless it has been patched already. """
            if model not in patched_models[name]:
                patched_models[name].add(model)
                model._patch_method(name, method)

        # retrieve base_conf, and patch forbidden models
        for base_conf in self.with_context({}).search([]):
            forbidden_models = base_conf.forbidden_models
            fbd_models_name = forbidden_models and \
                map(str.strip, str(forbidden_models).split(',')) or []
            for model_name in fbd_models_name:
                try:
                    if model_name in self.env:
                        Model = self.env[model_name]
                        patch(Model, 'create', make_create())
                    else:
                        logger.warning(
                                'Model "%s" not exists or is not loaded yet' % model_name)
                except Exception as e:
                    logger.error(
                        'Model "%s" not exists. Error : %s' %
                        (model_name, e[0]))
