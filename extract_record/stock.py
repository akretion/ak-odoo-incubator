# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    def get_record(self, cr, uid, browse, models, fields, context=None):
        values = {}
        excluded_fields = [
            'message_follower_ids', 'message_ids',
            'message_is_follower', 'message_summary']
        columns = browse._columns.keys()
        for elm in columns:
            if elm in excluded_fields:
                continue
            if browse._columns[elm]._type == 'many2many':
                models.extend([x for x in browse[elm]])
            if browse._columns[elm]._type == 'one2many':
                models.extend([x for x in browse[elm]])
            if browse._columns[elm]._type == 'many2one':
                if elm not in fields and not browse._columns[elm].required:
                    continue
                else:
                    models.append(browse[elm])
            if browse[elm]:
                values[elm] = browse[elm]
        return values

    def get_record_set(self, cr, uid, ids, context=None):
        excluded_models = ['res.company', 'res.users']
        if len(ids) > 1:
            raise orm.except_orm("Warning", "Only one record at once")
        browse = self.browse(cr, uid, ids, context=context)[0]
        records = {}
        models = []
        all_models = []
        fields = []
        records[self._name] = self.get_record(
            cr, uid, browse, models, ['partner_id'], context=context)
        all_models = list(set(models))
        models = []
        for elm in all_models:
            if elm._name in excluded_models:
                continue
            records[elm] = self.get_record(
                cr, uid, elm, models, fields, context=context)
        models = list(set(models))
        all_models.extend(models)
        raise orm.except_orm("Records", 'models:\n%s\n\nrecords:\n%s' % (
            all_models, records))
