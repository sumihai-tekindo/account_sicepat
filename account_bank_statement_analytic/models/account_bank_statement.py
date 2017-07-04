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

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'

    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', ondelete='set null', domain=[('type','!=','view'), ('state','not in',('close','cancelled'))]),
    }

    def process_reconciliation(self, cr, uid, id, mv_line_dicts, context=None):
        if context is None:
            context = {}
        st_line = self.browse(cr, uid, id, context=context)
        for mv_line_dict in mv_line_dicts:
            if not mv_line_dict.get('analytic_account_id'):
                mv_line_dict['analytic_account_id'] = st_line.analytic_account_id and st_line.analytic_account_id.id or False
        return super(account_bank_statement_line, self).process_reconciliation(cr, uid, id, mv_line_dicts, context=context)