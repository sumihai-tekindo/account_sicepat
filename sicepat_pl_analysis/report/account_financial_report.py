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

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header
from openerp.tools.translate import _
from openerp.osv import osv


class report_financial_sicepat_pl_analysis(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(report_financial_sicepat_pl_analysis, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'get_lines': self.get_lines,
            'time': time,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        res_company = self._get_res_company(data)
        self.localcontext.update({
            'res_company': res_company,
        })
        return super(report_financial_sicepat_pl_analysis, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_res_company(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).company_id
        return False
    
    def get_lines(self, data):
        lines = []
        account_obj = self.pool.get('account.account')
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]], context=data['form']['used_context'])
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=data['form']['used_context']):
            vals = {
                'name': report.name,
                'balance': {},
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type =='sum' and 'view' or False, #used to underline the financial report balances
            }
            for i in range(12):
                data['form']['used_context'].update(data['form'][str(i)]) 
                report_id = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=data['form']['used_context'])
                vals['balance'][str(i)] = data['form'][str(i)]['date_from'] and report_id.balance * report.sign or 0.0 
            lines.append(vals)
            account_ids = []
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(self.cr, self.uid, [x.id for x in report.account_ids])
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(self.cr, self.uid, [('user_type','in', [x.id for x in report.account_type_ids])])
            if account_ids:
                for account in account_obj.browse(self.cr, self.uid, account_ids, context=data['form']['used_context']):
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    if report.display_detail == 'detail_flat' and account.type == 'view':
                        continue
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': {},
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and min(account.level + 1,6) or 6, #account.level + 1
                        'account_type': account.type,
                    }
                    for i in range(12):
                        data['form']['used_context'].update(data['form'][str(i)]) 
                        account_id = account_obj.browse(self.cr, self.uid, account.id, context=data['form']['used_context'])
                        vals['balance'][str(i)] = data['form'][str(i)]['date_from'] and (account_id.balance != 0 and account_id.balance * report.sign or account_id.balance) or 0.0 
                    lines.append(vals)
        return lines


class report_financial_sicepat_pl_analysis_xls(report_xls):
    column_sizes = [42, 16, 9, 16, 9, 16, 9, 16, 9, 16, 9, 16, 9, 16, 9, 16, 9, 16, 9, 16, 9, 16, 9, 16, 9]

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(report_financial_sicepat_pl_analysis_xls, self).__init__(name, table, rml=rml, parser=parser, header=header, store=store)

    def print_empty_row(self, ws, row_position):
        # Print empty row to define column sizes
        c_sizes = self.column_sizes
        c_specs = [
            ('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, set_column_size=True)
        return row_position

    def print_title(self, ws, _p, row_position, xlwt, _xs):
        cell_style = xlwt.easyxf(_xs['xls_title'])
        report_name = 'Analisa Laporan Rugi Laba'
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf(_xs['bold'])
        company_name = _p.res_company.name
        c_specs = [
            ('company_name', 1, 0, 'text', company_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)

        row_position = self.print_empty_row(ws, row_position)
        return row_position

    def print_header_attributes(self, ws, _p, data, row_position, xlwt, _xs):
        fy = _('Fiscal Year: ')
        fy += _p.get_fiscalyear(data)
        c_specs = [
            ('fy', 1, 0, 'text', fy),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data)

        filters = _('Filter By: ')
        if data['form']['filter'] == 'filter_no': filters += _('Not filtered')
        if data['form']['filter'] == 'filter_period': filters += _('Filtered by period (') + _p.get_start_period(data) + _(' ') + _p.get_end_period(data) + _(')')
        if data['form']['filter'] == 'filter_date': filters += _('Filtered by date (') + _p.formatLang(_p.get_start_date(data), date=True) + _(' ') + _p.formatLang(_p.get_end_date(data), date=True) + _(')')
        c_specs = [
            ('filters', 1, 0, 'text', filters),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data)
        
        tm = _('Target Moves: ')
        tm += _p.get_target_move(data)
        c_specs = [
            ('tm', 1, 0, 'text', tm),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data)
       
        row_position = self.print_empty_row(ws, row_position)
        return row_position

    def print_header_titles(self, ws, _p, data, row_position, xlwt, _xs):
        cell_format = _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format + _xs['fill_blue'] + _xs['bold'] + _xs['center'])

        c_specs = [
            ('name', 1, 0, 'text', _('Nama Perkiraan'), None, cell_style),
            ('0', 2, 0, 'text', data['form']['0']['name'], None, cell_style),
            ('1', 2, 0, 'text', data['form']['1']['name'], None, cell_style),
            ('2', 2, 0, 'text', data['form']['2']['name'], None, cell_style),
            ('3', 2, 0, 'text', data['form']['3']['name'], None, cell_style),
            ('4', 2, 0, 'text', data['form']['4']['name'], None, cell_style),
            ('5', 2, 0, 'text', data['form']['5']['name'], None, cell_style),
            ('6', 2, 0, 'text', data['form']['6']['name'], None, cell_style),
            ('7', 2, 0, 'text', data['form']['7']['name'], None, cell_style),
            ('8', 2, 0, 'text', data['form']['8']['name'], None, cell_style),
            ('9', 2, 0, 'text', data['form']['9']['name'], None, cell_style),
            ('10', 2, 0, 'text', data['form']['10']['name'], None, cell_style),
            ('11', 2, 0, 'text', data['form']['11']['name'], None, cell_style),
        ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        c_specs = [
            ('name', 1, 0, 'text', _(''), None, cell_style),
            ('0_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('0_p', 1, 0, 'text', _('%'), None, cell_style),
            ('1_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('1_p', 1, 0, 'text', _('%'), None, cell_style),
            ('2_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('2_p', 1, 0, 'text', _('%'), None, cell_style),
            ('3_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('3_p', 1, 0, 'text', _('%'), None, cell_style),
            ('4_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('4_p', 1, 0, 'text', _('%'), None, cell_style),
            ('5_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('5_p', 1, 0, 'text', _('%'), None, cell_style),
            ('6_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('6_p', 1, 0, 'text', _('%'), None, cell_style),
            ('7_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('7_p', 1, 0, 'text', _('%'), None, cell_style),
            ('8_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('8_p', 1, 0, 'text', _('%'), None, cell_style),
            ('9_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('9_p', 1, 0, 'text', _('%'), None, cell_style),
            ('10_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('10_p', 1, 0, 'text', _('%'), None, cell_style),
            ('11_n', 1, 0, 'text', _('Nilai'), None, cell_style),
            ('11_p', 1, 0, 'text', _('%'), None, cell_style),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        return row_position

    def print_row_data(self, ws, _p, row_line, row_position, row_1, xlwt, _xs):
        cell_format = _xs['borders_all'] 
        if not row_line.get('level') > 1:
            cell_format += _xs['bold']
        _xs['indent'] = 'align: inde %s;' % (row_line.get('level', 0))
        cell_style = xlwt.easyxf(cell_format + _xs['indent'])
        cell_style_percentage = xlwt.easyxf(cell_format + _xs['right'], num_format_str='0.0%')
        cell_style_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str=report_xls.decimal_format)
        cell_style_currency = xlwt.easyxf(cell_format + _xs['right'], num_format_str='_(%s* #,##0.00_);_(%s* (#,##0.00);_(%s* "-"??_);_(@_)' % (_p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol))

        c_specs = [
            ('name', 1, 0, 'text', row_line['name'], None, cell_style),
            ('0_n', 1, 0, 'number', row_line['balance']['0'], None, cell_style_decimal),
            ('0_p', 1, 0, 'number', None, 'IF($B$'+str(row_1)+'=0;0;B'+str(row_position+1)+'/$B$'+str(row_1)+')', cell_style_percentage),
            ('1_n', 1, 0, 'number', row_line['balance']['1'], None, cell_style_decimal),
            ('1_p', 1, 0, 'number', None, 'IF($D$'+str(row_1)+'=0;0;D'+str(row_position+1)+'/$D$'+str(row_1)+')', cell_style_percentage),
            ('2_n', 1, 0, 'number', row_line['balance']['2'], None, cell_style_decimal),
            ('2_p', 1, 0, 'number', None, 'IF($F$'+str(row_1)+'=0;0;F'+str(row_position+1)+'/$F$'+str(row_1)+')', cell_style_percentage),
            ('3_n', 1, 0, 'number', row_line['balance']['3'], None, cell_style_decimal),
            ('3_p', 1, 0, 'number', None, 'IF($H$'+str(row_1)+'=0;0;H'+str(row_position+1)+'/$H$'+str(row_1)+')', cell_style_percentage),
            ('4_n', 1, 0, 'number', row_line['balance']['4'], None, cell_style_decimal),
            ('4_p', 1, 0, 'number', None, 'IF($J$'+str(row_1)+'=0;0;J'+str(row_position+1)+'/$J$'+str(row_1)+')', cell_style_percentage),
            ('5_n', 1, 0, 'number', row_line['balance']['5'], None, cell_style_decimal),
            ('5_p', 1, 0, 'number', None, 'IF($L$'+str(row_1)+'=0;0;L'+str(row_position+1)+'/$L$'+str(row_1)+')', cell_style_percentage),
            ('6_n', 1, 0, 'number', row_line['balance']['6'], None, cell_style_decimal),
            ('6_p', 1, 0, 'number', None, 'IF($N$'+str(row_1)+'=0;0;N'+str(row_position+1)+'/$N$'+str(row_1)+')', cell_style_percentage),
            ('7_n', 1, 0, 'number', row_line['balance']['7'], None, cell_style_decimal),
            ('7_p', 1, 0, 'number', None, 'IF($P$'+str(row_1)+'=0;0;P'+str(row_position+1)+'/$P$'+str(row_1)+')', cell_style_percentage),
            ('8_n', 1, 0, 'number', row_line['balance']['8'], None, cell_style_decimal),
            ('8_p', 1, 0, 'number', None, 'IF($R$'+str(row_1)+'=0;0;R'+str(row_position+1)+'/$R$'+str(row_1)+')', cell_style_percentage),
            ('9_n', 1, 0, 'number', row_line['balance']['9'], None, cell_style_decimal),
            ('9_p', 1, 0, 'number', None, 'IF($T$'+str(row_1)+'=0;0;T'+str(row_position+1)+'/$T$'+str(row_1)+')', cell_style_percentage),
            ('10_n', 1, 0, 'number', row_line['balance']['10'], None, cell_style_decimal),
            ('10_p', 1, 0, 'number', None, 'IF($V$'+str(row_1)+'=0;0;V'+str(row_position+1)+'/$V$'+str(row_1)+')', cell_style_percentage),
            ('11_n', 1, 0, 'number', row_line['balance']['11'], None, cell_style_decimal),
            ('11_p', 1, 0, 'number', None, 'IF($X$'+str(row_1)+'=0;0;X'+str(row_position+1)+'/$X$'+str(row_1)+')', cell_style_percentage),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        return row_position

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet('pl.analysis')
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape = 0
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        row_pos = self.print_title(ws, _p, row_pos, xlwt, _xs)
        
        row_pos = self.print_header_attributes(ws, _p, data, row_pos, xlwt, _xs)

        row_pos = self.print_header_titles(ws, _p, data, row_pos, xlwt, _xs)

        row_line_one = row_pos + 1
        for row_data in _p.get_lines(data):
            if row_data['level'] != 0:
                row_pos = self.print_row_data(ws, _p, row_data, row_pos, row_line_one, xlwt, _xs)


report_financial_sicepat_pl_analysis_xls('report.account.sicepat_pl_analysis_xls', 'account.account', parser=report_financial_sicepat_pl_analysis)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
