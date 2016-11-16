# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Pambudi Satria (<https://github.com/pambudisatria>).
#    @author Pambudi Satria <pambudi.satria@yahoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api
from openerp.tools.translate import _

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    current_revision_id = fields.Many2one('account.invoice', 'Current revision', readonly=True, copy=True)
    old_revision_ids = fields.One2many('account.invoice', 'current_revision_id', 'Old revisions', readonly=True, context={'active_test': False})
    revision_number = fields.Integer('Revision', copy=False)
    unrevisioned_name = fields.Char('Invoice Reference', copy=False, readonly=True)
    active = fields.Boolean('Active', default=True, copy=True)

    _sql_constraints = [
        ('revision_unique', 'unique(unrevisioned_name, revision_number, company_id)', 'Invoice Reference and revision must be unique per Company.'),
    ]

    @api.multi
    def action_cancel_draft(self):
        self.ensure_one()
        old_revision = self.with_context(new_invoice_revision=True).copy()
        view_ref = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
        view_id = view_ref and view_ref[1] or False,
        self.delete_workflow()
        self.create_workflow()
        self.write({'state': 'draft'})
        msg = _('New revision created: %s') % self.internal_number
        self.message_post(body=msg)
        old_revision.message_post(body=msg)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Customer Invoice'),
            'res_model': 'account.invoice',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('new_invoice_revision'):
            prev_number = self.internal_number
            revno = self.revision_number
            self.write({
                'revision_number': revno + 1,
                'internal_number': '%s-%02d' % (self.unrevisioned_name, revno + 1)
            })
            defaults.update({
                'internal_number': prev_number,
                'revision_number': revno,
                'active': False,
                'state': 'cancel',
                'current_revision_id': self.id,
                'unrevisioned_name': self.unrevisioned_name,
                'date_invoice': self.date_invoice,
            })
        return super(account_invoice, self).copy(defaults)

    @api.multi
    def action_number(self):
        #TODO: not correct fix but required a fresh values before reading it.
        self.write({})

        for inv in self:
            self.write({'internal_number': inv.number})

            if not inv.unrevisioned_name:
                self.write({'unrevisioned_name': inv.number})
                
            if inv.type in ('in_invoice', 'in_refund'):
                if not inv.reference:
                    ref = inv.number
                else:
                    ref = inv.reference
            else:
                ref = inv.number

            self._cr.execute(""" UPDATE account_move SET ref=%s
                           WHERE id=%s AND (ref IS NULL OR ref = '')""",
                        (ref, inv.move_id.id))
            self._cr.execute(""" UPDATE account_move_line SET ref=%s
                           WHERE move_id=%s AND (ref IS NULL OR ref = '')""",
                        (ref, inv.move_id.id))
            self._cr.execute(""" UPDATE account_analytic_line SET ref=%s
                           FROM account_move_line
                           WHERE account_move_line.move_id = %s AND
                                 account_analytic_line.move_id = account_move_line.id""",
                        (ref, inv.move_id.id))
            self.invalidate_cache()

        return True
