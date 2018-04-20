# coding: utf-8

from odoo import models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def set_coa4demo(self):
        if not self.env.context.get('install_mode'):
            return
        chart_tmpl_id = self.env.ref('account.configurable_chart_template')
        for key in ['a', 'b']:
            xml_id = 'multi_company_holding_invoicing.child_company_%s' % key
            company = self.env.ref(xml_id)
            # config = self.browse()
            import pdb; pdb.set_trace()
            vals = self.play_onchange({}, ['company_id'])
            # vals = config.onchange_company_id(company.id)['value']
            if not vals.get('has_chart_of_accounts'):
                vals['company_id'] = company.id
                vals['chart_template_id'] = chart_tmpl_id.id
                vals = self.play_onchange(vals, ['company_id'])
                # vals.update(config.onchange_chart_template_id(chart_tmpl_id.id))
                config = self.create(vals)
                config.execute()
