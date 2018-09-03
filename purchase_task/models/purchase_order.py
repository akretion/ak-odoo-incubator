# coding: utf-8
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    task_id = fields.Many2one(
        comodel_name='project.task', string='Related task',
        store=True,
        copy=False,
    )

    project_id = fields.Many2one(
        related="task_id.project_id",
        readonly=True)

    stage_id = fields.Many2one(
        related="task_id.stage_id",
        comodel_name='project.task.type',
        store=True,
        index=True,
    )

    stage_delivery = fields.Selection([
        ('waiting', 'Waiting'),
        ('available', 'Available'),
        ('done', 'Done'),
    ], compute='_compute_stage_delivery',
        store=True,
        index=True)

    stage_manufacture = fields.Selection([
        ('not applicable', 'Not Applicable'),
        ('waiting', 'Waiting Materials'),
        ('running', 'MRP Running'),
        ('done', 'Done'),
    ], compute='_compute_stage_manufacture',
        store=True,
        index=True)

    @api.depends('order_line.move_ids', 'order_line.move_ids.state')
    def _compute_stage_delivery(self):
        # done = all done
        # available : at least one available
        # waiting : the rest
        for rec in self:
            states = set(
                rec.picking_ids.filtered(
                    lambda x: x.picking_type_code == 'incoming'
                ).mapped('state'))
            if set(['done', 'cancel']) == states | set(['cancel']):
                rec.stage_delivery = 'done'
            elif 'assigned' in states:
                rec.stage_delivery = 'available'
            else:
                rec.stage_delivery = 'waiting'

    @api.depends(
        'order_line.procurement_ids.production_id.availability',
        'order_line.procurement_ids.production_id.state')
    def _compute_stage_manufacture(self):
        # done = all manufactures done
        # mrp running  = materials available or prod started
        # waiting = waiting availablity of materials
        # not applicable = no mrp linked in this po
        for rec in self:
            if rec.mo_count == 0:
                rec.stage_manufacture = 'not applicable'
                continue
            mo_states = set(rec.manufacture_ids.mapped('state'))
            if set(['done', 'cancel']) == mo_states | set(['cancel']):
                rec.stage_manufacture = 'done'
                continue
            availability_states = rec.manufacture_ids.mapped('availability')
            if 'waiting' in availability_states:
                rec.stage_manufacture = 'waiting'
            else:
                rec.stage_manufacture = 'running'

    def _set_task(self):
        purchase_project = self.env.ref('purchase_task.purchase_project')
        for rec in self:
            if not rec.task_id:
                vals = {
                    'project_id': purchase_project.id,
                    'name': rec.name,
                    'user_id': rec.env.uid,
                    'partner_id': rec.partner_id.id,
                }
                task = self.env['project.task'].create(vals)
                rec.task_id = task
        return task

    @api.model
    def create(self, values):
        # create is called when save button is hit.
        res = super(PurchaseOrder, self).create(values)
        res._set_task()
        return res

    @api.multi
    def write(self, values):
        # TODO: faire une nouvelle classe pour avoir des api depends
        res = super(PurchaseOrder, self).write(values)
        for rec in self:
            if rec.task_id and 'partner_id' in values:
                # update responsible of the task
                rec.task_id.partner_id = rec.partner_id
            if rec.task_id and 'state' in values:
                # archive task related to cancelled PO
                if values['state'] == 'cancel':
                    rec.task_id.active = False
                if values['state'] == 'draft':
                    rec.task_id.active = True
        return res

    @api.multi
    def action_view_task(self):
        '''Display existing purchase task'''
        action = self.env.ref('project.act_project_project_2_project_task_all')
        res = self.env.ref('project.view_task_form2', False)
        result = action.read()[0]
        result['context'] = {}
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.task_id.id
        return result
