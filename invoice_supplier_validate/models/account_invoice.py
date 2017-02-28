# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 STI (<https://github.com/sumihai-tekindo>).
#    @author: - Pambudi Satria <pambudi.satria@yahoo.com>
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

# 1 : imports of python lib


# 2 :  imports of openerp
from openerp import models, fields, api, _

# 3 :  imports from odoo modules
class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    state = fields.Selection(related='invoice_id.state', default='draft')

    @api.multi
    def unlink(self):
        for line in self:
            if line.state not in ('draft', 'cancel'):
                raise Warning(_('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))
            elif line.invoice_id.internal_number:
                raise Warning(_('You cannot delete an invoice after it has been validated (and received a number).  You can set it back to "Draft" state and modify its content, then re-confirm it.'))
        return super(AccountInvoiceLine, self).unlink()

class AccountInvoice(models.Model):
    # Private attributes
    _inherit = "account.invoice"
    
    # Default methods


    # Fields declaration
    invoice_line = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines',
        readonly=True, states={'draft': [('readonly', False)],'approved': [('readonly', False)]}, copy=True)
    state = fields.Selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('submit','Submit'),
            ('acknowledge','Acknowledge'),
            ('approved','Approve'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    
    # compute and search fields, in the same order that fields declaration

            
    # Constraints and onchanges


    # CRUD methods


    # Action methods
#     @api.multi
#     def invoice_submit(self):
#         return self.write({'state': 'submit'})
# 
#     @api.multi
#     def invoice_acknowledge(self):
#         return self.write({'state': 'acknowledge'})
# 
#     @api.multi
#     def invoice_approve(self):
#         return self.write({'state': 'approved'})

    # Business methods
