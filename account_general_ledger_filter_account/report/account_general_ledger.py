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

from openerp.osv import osv
from openerp.tools.translate import _
# from openerp.report import report_sxw
from openerp.addons.account.report.account_general_ledger import general_ledger as gnrl_ldgr

class general_ledger(gnrl_ldgr):

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        obj_move = self.pool.get('account.move.line')
        self.sortby = data['form'].get('sortby', 'sort_date')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context',{}))
        ctx2 = data['form'].get('used_context',{}).copy()
        self.init_balance = data['form'].get('initial_balance', True)
        if self.init_balance:
            ctx2.update({'initial_bal': True})
        self.display_account = data['form']['display_account']
        self.target_move = data['form'].get('target_move', 'all')
        context = dict(self.context)
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
        self.context = context.update(ctx)
        self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        if (data['model'] == 'ir.ui.menu') and data['form'].get('all_account') is False and data['form'].get('account_ids'):
            data['model'] = 'account.account'
            new_ids = data['form']['account_ids']
            data.update({'ids': new_ids})
            data['form'].update({'active_ids': new_ids})
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        if (data['model'] == 'ir.ui.menu'):
            new_ids = [data['form']['chart_account_id']]
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(gnrl_ldgr, self).set_context(objects, data, new_ids, report_type=report_type)
    
        
class report_generalledger(osv.AbstractModel):
    _name = 'report.account.report_generalledger'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger'
    _wrapped_report_class = general_ledger


