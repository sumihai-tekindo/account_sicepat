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

from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
import pytz
import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

_as_date = {
    'days': lambda as_of_date, val: as_of_date + relativedelta(days=-val),
    'weeks': lambda as_of_date, val: as_of_date + relativedelta(weeks=-val),
    'months': lambda as_of_date, val: as_of_date + relativedelta(months=-val),
}

class parser_customer_churn(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(parser_customer_churn, self).__init__(cr, uid, name, context=context)

    def set_context(self, objects, data, ids, report_type=None):
        self.as_of_date = data['form'].get('as_of_date')
        self.interval_number = data['form'].get('interval_cust_churn_number')
        self.interval_type = data['form'].get('interval_cust_churn_type')
        display_rev_head_1 = self.get_rev_head_1()
        display_rev_head_2 = self.get_rev_head_2()
        lines = self.lines()
        self.localcontext.update({
            'display_rev_head_1': lambda: display_rev_head_1,
            'display_rev_head_2': lambda: display_rev_head_2,
            'lines': lambda: lines,
        })
        return super(parser_customer_churn, self).set_context(objects, data, ids, report_type=report_type)

    def get_rev_head_1(self):
        return _('Revenue %s %s ago' % (self.interval_number *2, self.interval_type))

    def get_rev_head_2(self):
        return _('Revenue %s %s ago' % (self.interval_number, self.interval_type))

    def lines(self):
        partner = self.pool.get('res.partner')
        move_line = self.pool.get('account.move.line')
        analytic_account = self.pool.get('account.analytic.account')
        analytic_line = self.pool.get('account.analytic.line')
        result = []
        number_val_1 = self.interval_number * 2
        number_val_2 = self.interval_number
        as_of_date_1 = str(_as_date[self.interval_type](datetime.strptime(self.as_of_date, DF), number_val_1))[:10]
        as_of_date_2 = str(_as_date[self.interval_type](datetime.strptime(self.as_of_date, DF), number_val_2))[:10]
        account_income = self.pool.get('ir.property').get(self.cr, self.uid, 'property_account_income_categ', 'product.category')
        cust_ids = partner.search(self.cr, self.uid, [('customer', '=', True)], order='name asc')
        for customer in partner.browse(self.cr, self.uid, cust_ids):
            all_data = {}
            domain = [('partner_id', '=', customer.id), ('account_id', '=', account_income.id)]
            domain_1 = [('date', '<', as_of_date_2), ('date', '>=', as_of_date_1)]
            domain_2 = [('date', '<', self.as_of_date), ('date', '>=', as_of_date_2)]
            bal_1 = 0.0
            bal_2 = 0.0
            
            all_data['partner_id'] = customer.id
            all_data['partner_name'] = customer.name
            all_data['user_id'] = customer.user_id.id
            all_data['user_name'] = customer.user_id.name
            all_data['balance_1'] = {}
            all_data['balance_2'] = {}
            move_line_ids_1 = move_line.search(self.cr, self.uid, domain + domain_1)
            if move_line_ids_1:
                self.cr.execute("SELECT DISTINCT account_id FROM account_analytic_line WHERE move_id IN %s ORDER BY account_id", (tuple(move_line_ids_1),))
                analytic_ids_1 = [a for (a,) in self.cr.fetchall()]
                for analytic_id_1 in analytic_ids_1:
                    analytic_account_1 = analytic_account.browse(self.cr, self.uid, [analytic_id_1])
                    analytic_line_ids_1 = analytic_line.search(self.cr, self.uid, [('account_id', '=', analytic_id_1), ('move_id', 'in', move_line_ids_1)])
                    analytic_line_1 = analytic_line.browse(self.cr, self.uid, analytic_line_ids_1)
                    bal_1 = sum(al.amount for al in analytic_line_1)
                    all_data['balance_1'][str(analytic_id_1)] = {'name': analytic_account_1.complete_name, 'balance': bal_1} 
            
            move_line_ids_2 = move_line.search(self.cr, self.uid, domain + domain_2)
            if move_line_ids_2:
                self.cr.execute("SELECT DISTINCT account_id FROM account_analytic_line WHERE move_id IN %s ORDER BY account_id", (tuple(move_line_ids_2),))
                analytic_ids_2 = [a for (a,) in self.cr.fetchall()]
                for analytic_id_2 in analytic_ids_2:
                    analytic_account_2 = analytic_account.browse(self.cr, self.uid, [analytic_id_2]) 
                    analytic_line_ids_2 = analytic_line.search(self.cr, self.uid, [('account_id', '=', analytic_id_2), ('move_id', 'in', move_line_ids_2)])
                    analytic_line_2 = analytic_line.browse(self.cr, self.uid, analytic_line_ids_2)
                    bal_2 = sum(al.amount for al in analytic_line_2)
                    all_data['balance_2'][str(analytic_id_2)] = {'name': analytic_account_2.complete_name, 'balance': bal_2} 
            
            if all_data['balance_1']:
                for key_id in all_data['balance_1']:
                    balance_1 = all_data['balance_1'][key_id]['balance']
                    balance_2 = 0.0
                    if all_data['balance_2'].get(key_id, False):
                        balance_2 = all_data['balance_2'][key_id]['balance']
                    if balance_2 < balance_1:
                        new_data = {}
                        new_data['partner_id'] = all_data['partner_id']
                        new_data['partner_name'] = all_data['partner_name']
                        new_data['user_id'] = all_data['user_id']
                        new_data['user_name'] = all_data['user_name']
                        new_data['analytic_id'] = int(key_id)
                        new_data['analytic_name'] = all_data['balance_1'][key_id]['name']
                        new_data['balance_1'] = balance_1
                        new_data['balance_2'] = balance_2
                        churn_rate = (balance_1 - balance_2) / balance_1
                        new_data['churn_rate'] = churn_rate
                        result.append(new_data)
        
        result = sorted(result, key=lambda k: (k['churn_rate'], k['partner_name']))            
        return result

class customer_churn_report(report_xls):
    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(customer_churn_report, self).__init__(name, table, rml=rml, parser=parser, header=header, store=store)

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet('customer.churn')
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape = 0
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        report_name = 'Laporan Pergerakan Revenue Customer yang Menurun'
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

        # write empty row to define column sizes
        c_sizes = [10,25,45,15,15,15,12]
        c_specs = [
            ('empty%s' % i, 1, c_sizes[i], 'text', None) for i in range(0, len(c_sizes))
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, set_column_size=True)

        # Column Header Row
        cell_format = _xs['borders_all']
        _xs['center_wrap'] = 'align: horz center; align: vert center; align: wrap true;'
        c_hdr_cell_style_center = xlwt.easyxf(cell_format + _xs['fill'] + _xs['bold'] + _xs['center_wrap'])
        c_specs = [
            ('number', 1, 0, 'text', _('No'), None, c_hdr_cell_style_center),
            ('cust_name', 1, 0, 'text', _('Pelanggan'), None, c_hdr_cell_style_center),
            ('analytic_account', 1, 0, 'text', _('Gerai'), None, c_hdr_cell_style_center),
            ('user_name', 1, 0, 'text', _('Nama Sales'), None, c_hdr_cell_style_center),
            ('revenue_1', 1, 0, 'text', _p.display_rev_head_1(), None, c_hdr_cell_style_center),
            ('revenue_2', 1, 0, 'text', _p.display_rev_head_2(), None, c_hdr_cell_style_center),
            ('percentage', 1, 0, 'text', _('Percentage'), None, c_hdr_cell_style_center),
        ]
        c_hdr_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, c_hdr_data, row_style=c_hdr_cell_style_center)
        
        # Column Line Rows
        c_line_cell_style = xlwt.easyxf(cell_format)
        c_line_cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_line_cell_style_percentage = xlwt.easyxf(cell_format + _xs['right'], num_format_str='0.0%')
        c_line_cell_style_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str=report_xls.decimal_format)

        line_row = 1
        for line in _p.lines():
            c_specs = [
                ('number', 1, 0, 'number', line_row, None, c_line_cell_style_center),
                ('cust_name', 1, 0, 'text', line['partner_name'], None, c_line_cell_style),
                ('analytic_account', 1, 0, 'text', line['analytic_name'], None, c_line_cell_style),
                ('user_name', 1, 0, 'text', line['user_name'], None, c_line_cell_style),
                ('revenue_1', 1, 0, 'number', line['balance_1'], None, c_line_cell_style_decimal),
                ('revenue_2', 1, 0, 'number', line['balance_2'], None, c_line_cell_style_decimal),
                ('percentage', 1, 0, 'number', line['churn_rate'], None, c_line_cell_style_percentage),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_line_cell_style)
            line_row += 1

customer_churn_report('report.customer.churn.report.xls', 'account.move.line', parser=parser_customer_churn)