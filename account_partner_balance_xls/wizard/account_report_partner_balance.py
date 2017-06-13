# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 STI (<https://github.com/sumihai-tekindo>).
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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_partner_balance(osv.osv_memory):
    _inherit = 'account.partner.balance'

    _columns = {
        'display_detail': fields.boolean('Display Detail'),
        'all_partner': fields.boolean('All Partner?'),
        'report_type': fields.selection([
            ('xls','Excel'),
            ('pdf','PDF')
            ], 'Report Type', required=True),
        'partner_ids': fields.many2many('res.partner', string='Partners'),
    }
    _defaults = {
        'display_detail': False,
        'all_partner': True,
        'report_type': 'xls',
    }

    def onchange_result_selection(self, cr, uid, ids, res_select='customer', context=None):
        res = {'domain': {'partner_ids': [('customer', '=', True)]}}
        if res_select == 'customer_supplier':
            res = {'domain': {'partner_ids': [('customer', '=', True), ('supplier', '=', True)]}}
        if res_select == 'supplier':
            res = {'domain': {'partner_ids': [('supplier', '=', True)]}}
        return res
        
    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = super(account_partner_balance, self).pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['display_partner'])[0])
        return data

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}

        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['display_detail', 'all_partner', 'report_type', 'partner_ids'])[0])
        all_partner = 'all_partner' in data['form'] and data['form']['all_partner'] or False
        partner_ids = 'partner_ids' in data['form'] and data['form']['partner_ids'] or False
        data['form']['used_context'].update(dict(all_partner=all_partner, partner_ids=partner_ids))

        if data['form']['report_type'] == 'xls':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.report_partnerbalance_xls',
                'datas': data
            }
        return self.pool['report'].get_action(cr, uid, [], 'account.report_partnerbalance', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
