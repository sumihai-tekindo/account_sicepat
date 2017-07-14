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
from openerp.osv import osv
from openerp.tools.translate import _
# from openerp.report import report_sxw
from openerp.addons.account.report.account_balance import account_balance as acct_bal

class account_balance(acct_bal):

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        ctx2 = data['form'].get('used_context',{}).copy()
        self.init_balance = data['form'].get('initial_balance', True)
        if self.init_balance:
            ctx2.update({'initial_bal': True})
        self.display_account = data['form']['display_account']
        self.target_move = data['form'].get('target_move', 'all')
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form']['fiscalyear_id']
        if data['form']['filter'] == 'filter_period':
            period_from_id = data['form']['period_from']
            period_to_id = data['form']['period_to']
            ctx['periods'] = self.pool["account.period"].build_ctx_periods(self.cr, self.uid, period_from_id, period_to_id)
            # Do not let "_query_get" calculate the periods itself
            ctx2.update({'periods': ctx['periods']})
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form']['date_from']
            ctx['date_to'] =  data['form']['date_to']
        ctx['state'] = data['form']['target_move']
        self.context.update(ctx)
        self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        self.localcontext.update( {
            'sum_initial_balance_account': self._sum_initial_balance_account,
        })
        return super(account_balance, self).set_context(objects, data, ids, report_type=report_type)
    
    def _sum_initial_balance_account(self, account):
        if account['type'] == 'view':
            return account['balance']
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        sum_balance = 0.0
        if self.init_balance:
            self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account['id'], tuple(move_state)))
            # Add initial balance to the result
            sum_balance += self.cr.fetchone()[0] or 0.0
        return sum_balance

        
class report_trialbalance(osv.AbstractModel):
    _name = 'report.account.report_trialbalance'
    _inherit = 'report.abstract_report'
    _template = 'account.report_trialbalance'
    _wrapped_report_class = account_balance

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
