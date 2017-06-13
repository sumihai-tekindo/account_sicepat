# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 STI (<https://github.com/sumihai-tekindo>).
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

class account_balance_report(osv.osv_memory):
    _inherit = 'account.balance.report'

    _columns = {
        'initial_balance': fields.boolean('Include Initial Balances',
                                    help='If you selected to filter by date or period, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.'),
    }
    _defaults = {
        'initial_balance': False,
    }

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False, context=None):
        res = {}
        if not fiscalyear:
            res['value'] = {'initial_balance': False}
        return res

    def _print_report(self, cr, uid, ids, data, context=None):
        context = dict(context or {})
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['initial_balance'])[0])
        if not data['form']['fiscalyear_id']:# GTK client problem onchange does not consider in save record
            data['form'].update({'initial_balance': False})
        if data['form'].get('initial_balance'):
            context['landscape'] = True

        return self.pool['report'].get_action(cr, uid, [], 'account.report_trialbalance', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
