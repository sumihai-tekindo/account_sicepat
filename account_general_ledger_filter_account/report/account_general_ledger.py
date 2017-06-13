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
        if (data['model'] == 'ir.ui.menu') and data['form'].get('all_account') is False and data['form'].get('account_ids'):
            data['model'] = 'account.account'
            new_ids = data['form']['account_ids']
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(general_ledger, self).set_context(objects, data, ids, report_type=report_type)
    
        
class report_generalledger(osv.AbstractModel):
    _name = 'report.account.report_generalledger'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger'
    _wrapped_report_class = general_ledger


