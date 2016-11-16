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

import time

from openerp.osv import fields, osv


class account_partner_balance(osv.osv_memory):
    """
        This wizard will provide the partner balance report by periods, between any two dates.
    """
    _inherit = 'account.common.partner.report'
    _name = 'account.partner.outstanding'
    _description = 'Print Outstanding Invoices'
    _columns = {
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date')], "Filter by", required=True),
        'date_as_of': fields.date("As of Date"),
        'show_only_date': fields.boolean("Show only this date?"),
        'display_partner': fields.selection([('non-zero_balance', 'With balance is not equal to 0'), ('all', 'All Partners')]
                                    ,'Display Partners'),
        'partner_ids': fields.many2many('res.partner', string='Partners'),
    }

    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        res = super(account_partner_balance, self).onchange_filter(cr, uid, ids, filter=filter, fiscalyear_id=fiscalyear_id, context=context)
        if filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False, 'date_to': False, 'date_as_of': False}
        if filter == 'filter_date':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False, 'date_to': False, 'date_as_of': time.strftime('%Y-%m-%d')}
        return res

    _defaults = {
        'display_partner': 'non-zero_balance',
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['date_as_of', 'show_only_date', 'display_partner', 'partner_ids'])[0])
        return self.pool['report'].get_action(cr, uid, [], 'account.report_partneroutstanding', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
