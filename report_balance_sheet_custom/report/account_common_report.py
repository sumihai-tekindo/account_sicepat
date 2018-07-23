##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp.report import report_sxw
from openerp.addons.account.report.account_financial_report import report_account_common
from openerp.tools.translate import _
from openerp.osv import osv


class report_account_common_inh(report_account_common):

    def set_context(self, objects, data, ids, report_type=None):
        self.localcontext.update({
            'get_columns': self._get_columns,
            'get_col_dict': self._get_col_dict,
            'get_group_lines': self.get_group_lines,
        })
        return super(report_account_common_inh, self).set_context(objects, data, ids, report_type=report_type)

    def get_lines(self, data):
        lines = super(report_account_common_inh, self).get_lines(data)
        for line in lines:
            if data['form']['enable_filter'] and data['form']['with_difference']:
                line['balance_diff'] = line.get('balance',0.0)-line.get('balance_cmp',0.0)
            if data['form']['enable_filter'] and data['form']['with_total']:
                line['balance_total']=line.get('balance',0.0)+line.get('balance_cmp',0.0)
        return lines

    def _get_model_group(self, key):
        if key == 'analytic':
            return 'account.analytic.account'
        if key == 'department':
            return 'account.invoice.department'
        return False

    def _get_domain_group(self, data):
        if data['form']['group_by'] == 'analytic':
            domain = [('tag', 'in', ('gerai', 'cabang', 'toko', 'head_office', 'agen', 'transit', 'pusat_transitan')), ('parent_id.tag', '=', 'kota')]
            if not data['form']['all_analytic'] and data['form']['analytic_ids']:
                domain = [('id', 'in', tuple(data['form']['analytic_ids']))]
            return domain
        if data['form']['group_by'] == 'department':
            domain = []
            if not data['form']['all_department'] and data['form']['department_ids']:
                domain = [('id', 'in', tuple(data['form']['department_ids']))]
            return domain
        return []
        
    def _get_col_dict(self, data):
        model = self._get_model_group(data['form']['group_by'])
        col_obj = self.pool.get(model)

        col_dict = dict()
        domain = self._get_domain_group(data)
        col_ids = col_obj.search(self.cr, self.uid, domain)
        for col in col_obj.browse(self.cr, self.uid, col_ids):
            if data['form']['group_by'] == 'analytic':
                col_dict.setdefault(col.code, dict(id=col.id,name=col.code,string=col.display_name))
            if data['form']['group_by'] == 'department':
                col_dict.setdefault(col.name, dict(id=col.id,name=col.name,string=col.description))
        col_dict.setdefault('', dict(id=False,name='',string='Undefined'))
        return col_dict

    def _get_columns(self, data):
        col_dict = self._get_col_dict(data)
        return list(col_dict)

    def get_group_lines(self, data):
        ctx = data['form']['used_context']
        col_dict = self._get_col_dict(data)
        account_obj = self.pool.get('account.account')
        lines = self.get_lines(data)
        for line in lines:
            for col in col_dict.keys():
                line.update({col: 0.0})
            if line['type'] == 'account':
                sign = line['balance'] < 0 and -1 or 1
                if data['form']['group_by'] == 'analytic':
                    ctx_key = 'analytic_ids'
                if data['form']['group_by'] == 'department':
                    ctx_key = 'department_ids'
                account_code = line['name'].split(' ')[0]
                account_id = account_obj.search(self.cr, self.uid, [('code', '=', account_code)])
                for k, v in col_dict.items():
                    ctx[ctx_key] = v['id'] and [v['id']] or False 
                    account = account_obj.browse(self.cr, self.uid, account_id, context=ctx)
                    line[k] = account.balance * sign
        return lines


class report_financial_inh(osv.AbstractModel):
    _name = 'report.account.report_financial'
    _inherit = 'report.abstract_report'
    _template = 'account.report_financial'
    _wrapped_report_class = report_account_common_inh
