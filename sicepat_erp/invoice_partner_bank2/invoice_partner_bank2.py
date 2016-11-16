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

class AccountInvoice(models.Model):
    # Private attributes
    _inherit = "account.invoice"

    # Default methods
#     @api.model
#     def _get_partner_bank(self):
#         inv_type = self._context.get('type', 'out_invoice')
#         partner_bank = self.env['ir.model.data'].get_object('l10n_id_sicepat', 'bank_2703027211')
#         if partner_bank and inv_type == 'out_invoice':
#             return partner_bank
#         return False
# 
#     @api.model
#     def _get_partner_bank2(self):
#         inv_type = self._context.get('type', 'out_invoice')
#         partner_bank2 = self.env['ir.model.data'].get_object('l10n_id_sicepat', 'bank_1640001045675')
#         if partner_bank2 and inv_type == 'out_invoice':
#             return partner_bank2
#         return False
#     
#     @api.model
#     def _get_comment(self):
#         partner_bank = self._get_partner_bank()
#         partner_bank2 = self._get_partner_bank2()
#         new_comment = ''
#         if partner_bank:
#             new_comment += 'Pembayaran dapat dilakukan melalui transfer ke:\n\n%s\n%s\n%s\n' % (partner_bank.bank_name.upper(), partner_bank.acc_number, partner_bank.owner_name.upper())
#         if partner_bank2:
#             new_comment += '\natau\n\n%s\n%s\n%s\n' % (partner_bank2.bank_name.upper(), partner_bank2.acc_number, partner_bank2.owner_name.upper())
#         return '%s' % (new_comment)
    
    # Fields declaration
    partner_bank_id = fields.Many2one(string='Bank Account #1',)
#     partner_bank_id = fields.Many2one(string='Bank Account #1', default=_get_partner_bank,)
    partner_bank2_id = fields.Many2one('res.partner.bank', string='Bank Account #2',
        help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Supplier Refund, otherwise a Partner bank account number.',
        readonly=True, states={'draft': [('readonly', False)]})
#     partner_bank2_id = fields.Many2one('res.partner.bank', string='Bank Account #2',
#         help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Supplier Refund, otherwise a Partner bank account number.',
#         default=_get_partner_bank2, readonly=True, states={'draft': [('readonly', False)]})
#     comment = fields.Text(default=_get_comment)
    