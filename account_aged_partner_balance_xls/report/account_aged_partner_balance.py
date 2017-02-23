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
from openerp.osv import osv
# from openerp.report import report_sxw
from openerp.addons.account.report.account_aged_partner_balance import aged_trial_report as atr

class aged_trial_report(atr):

    def __init__(self, cr, uid, name, context):
        super(aged_trial_report, self).__init__(cr, uid, name, context=context)

    def set_context(self, objects, data, ids, report_type=None):
        res_company = self._get_res_company(data)
        self.localcontext.update({
            'res_company': res_company,
        })
        return super(aged_trial_report, self).set_context(objects, data, ids, report_type=report_type)
    
    def _get_res_company(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).company_id
        return False