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

import openerp
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv

class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'

    _columns = {
#         'default_partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account #1',
#             help="Bank Account Number to which the invoice will be paid.", default_model='account.invoice'),
        'default_bank_id': fields.many2one('res.partner.bank', 'Bank Account #1',
            help="Bank Account Number to which the invoice will be paid."),
#         'default_partner_bank2_id': fields.many2one('res.partner.bank', 'Bank Account #2',
#             help="Bank Account Number to which the invoice will be paid.", default_model='account.invoice'),
        'default_bank2_id': fields.many2one('res.partner.bank', 'Bank Account #2',
            help="Bank Account Number to which the invoice will be paid."),
        'default_bank3_id': fields.many2one('res.partner.bank', 'Bank Account #3',
            help="Bank Account Number to which the invoice will be paid."),
        'default_bank4_id': fields.many2one('res.partner.bank', 'Bank Account #4',
            help="Bank Account Number to which the invoice will be paid."),

    }

    def get_default_partner_bank(self, cr, uid, fields, context=None):
        ir_values = self.pool.get('ir.values')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company_id = user.company_id.id
        condition = 'type=out_invoice'
        partner_bank_id = ir_values.get_default(cr, SUPERUSER_ID, 'account.invoice', 'partner_bank_id', company_id=company_id, condition=condition)
        partner_bank2_id = ir_values.get_default(cr, SUPERUSER_ID, 'account.invoice', 'partner_bank2_id', company_id=company_id, condition=condition)
        partner_bank3_id = ir_values.get_default(cr, SUPERUSER_ID, 'account.invoice', 'partner_bank3_id', company_id=company_id, condition=condition)
        partner_bank4_id = ir_values.get_default(cr, SUPERUSER_ID, 'account.invoice', 'partner_bank4_id', company_id=company_id, condition=condition)
        return {
            'default_bank_id': partner_bank_id,
            'default_bank2_id': partner_bank2_id,
            'default_bank3_id': partner_bank3_id,
            'default_bank4_id': partner_bank4_id,
        }
  
    def set_default_partner_bank(self, cr, uid, ids, context=None):
        """ set default partner bank for invoice """
        if uid != SUPERUSER_ID and not self.pool['res.users'].has_group(cr, uid, 'base.group_erp_manager'):
            raise openerp.exceptions.AccessError(_("Only administrators can change the settings"))
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids[0], context)
        partner_bank_id = config.default_bank_id and config.default_bank_id.id or False
        partner_bank2_id = config.default_bank2_id and config.default_bank2_id.id or False
        partner_bank3_id = config.default_bank3_id and config.default_bank3_id.id or False
        partner_bank4_id = config.default_bank4_id and config.default_bank4_id.id or False
        company_id = config.company_id.id
        condition = 'type=out_invoice'
        ir_values.set_default(cr, SUPERUSER_ID, 'account.invoice', 'partner_bank_id',
            partner_bank_id, company_id=company_id, condition=condition)
        ir_values.set_default(cr, SUPERUSER_ID, 'account.invoice', 'partner_bank2_id',
            partner_bank2_id, company_id=company_id, condition=condition)
        ir_values.set_default(cr, SUPERUSER_ID, 'account.invoice', 'partner_bank3_id',
            partner_bank3_id, company_id=company_id, condition=condition)
        ir_values.set_default(cr, SUPERUSER_ID, 'account.invoice', 'partner_bank4_id',
            partner_bank4_id, company_id=company_id, condition=condition)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
