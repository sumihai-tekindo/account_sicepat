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

from openerp.osv import fields, osv

class account_partner_balance(osv.osv_memory):
    _inherit = 'account.report.general.ledger'

    _columns = {
        'all_account': fields.boolean('All Accounts?'),
        'account_ids': fields.many2many('account.account', string='Accounts'),
        'all_department': fields.boolean('All Departments?'),
        'department_ids': fields.many2many('account.invoice.department', 'report_ledger_department_rel', 'did', 'rid',  string='Departments'),
        'all_analytic': fields.boolean('All Account Analytics?'),
        'analytic_ids': fields.many2many('account.analytic.account', 'report_ledger_analytic_rel', 'aid', 'rid', string='Analytic Accounts',
                                         domain=[('tag', 'in', ('gerai', 'cabang', 'toko', 'head_office', 'agen', 'transit', 'pusat_transitan'))]),
        'report_type': fields.selection([
            ('xlsx','XLSX'),
            ('pdf','PDF')
            ], 'Report Type', required=True),
    }
    _defaults = {
        'all_account': True,
        'all_department': True,
        'all_analytic': True,
        'report_type': 'xlsx',
   }

    def _print_report(self, cr, uid, ids, data, context=None):
        context = dict(context or {})
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['landscape',  'initial_balance', 'amount_currency', 'sortby', 'all_account', 'account_ids', 'all_department', 'department_ids', 'all_analytic', 'analytic_ids', 'report_type'])[0])
        if 'used_context' in data['form'] and not data['form']['all_department']:
            data['form']['used_context']['department_ids'] = 'department_ids' in data['form'] and data['form']['department_ids'] or False
        if 'used_context' in data['form'] and not data['form']['all_analytic']:
            data['form']['used_context']['analytic_ids'] = 'analytic_ids' in data['form'] and data['form']['analytic_ids'] or False
        if not data['form']['fiscalyear_id']:# GTK client problem onchange does not consider in save record
            data['form'].update({'initial_balance': False})

        if data['form']['landscape'] is False:
            data['form'].pop('landscape')
        else:
            context['landscape'] = data['form']['landscape']

        if data['form']['report_type'] == 'xlsx':
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'account.report_generalledger_xlsx',
                    'datas': data
                }
        else:
            return self.pool['report'].get_action(cr, uid, [], 'account.report_generalledger', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
