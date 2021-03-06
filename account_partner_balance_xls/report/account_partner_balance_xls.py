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

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from .account_partner_balance import partner_balance
# from openerp.addons.account.report.account_aged_partner_balance import aged_trial_report
from openerp.tools.translate import _

class partner_balance_xls(report_xls):
    column_sizes = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    
    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(partner_balance_xls, self).__init__(name, table, rml=rml, parser=parser, header=header, store=store)
        
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
        report_name = 'Partner Balance'
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        
        row_position = self.print_empty_row(ws, row_position)
        return row_position

    def print_header_attributes(self, ws, _p, data, row_position, xlwt, _xs):
        cell_format = _xs['top']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_wrap = xlwt.easyxf(cell_format + _xs['wrap'])
        cell_style_bold = xlwt.easyxf(_xs['bold'])
        c_specs = [
            ('coa', 3, 0, 'text', _('Chart of Accounts:')),
            ('fy', 3, 0, 'text', _('Fiscal Year:')),
            ('jrn', 3, 0, 'text', _('Journals:')),
            _p.get_partners() and ('part', 3, 0, 'text', _('Partner\'s')) or
            ('part', 3, 0, 'text', None),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style_bold)
        
        c_specs = [
            ('coa', 3, 0, 'text', _p.get_account(data)),
            ('fy', 3, 0, 'text', _p.get_fiscalyear(data)),
            ('jrn', 3, 0, 'text', ', '.join([ lt or '' for lt in _p.get_journal(data) ]), None, cell_style_wrap),
            _p.get_partners() and ('part', 3, 0, 'text', _p.get_partners()) or
            ('part', 3, 0, 'text', None),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        
        c_specs = [
            ('df', 3, 0, 'text', _('Filter By:')),
            ('tm', 3, 0, 'text', _('Target Moves:')),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style_bold)
        
        filter_by = _('')
        if data['form']['filter'] == 'filter_no': filter_by = _('Not filtered')
        if data['form']['filter'] == 'filter_period':
            filter_by = _('Filtered by period\n\n')
            filter_by += _('Start Period: %s\n' % _p.get_start_period(data))
            filter_by += _('End Period: %s' % _p.get_end_period(data))
        if data['form']['filter'] == 'filter_date':
            filter_by = _('Filtered by date\n\n')
            filter_by += _('Date from: %s\n' % _p.formatLang(_p.get_start_date(data), date=True))
            filter_by += _('Date to: %s' % _p.formatLang(_p.get_end_date(data), date=True))
        c_specs = [
            ('df', 3, 0, 'text', filter_by, None, cell_style_wrap),
            ('tm', 3, 0, 'text', _p.get_target_move(data)),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        
        row_position = self.print_empty_row(ws, row_position)
        return row_position

    def print_header_titles(self, ws, _p, data, row_position, xlwt, _xs):
        cell_format = _xs['bold'] + _xs['borders_bottom_black']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_right = xlwt.easyxf(cell_format + _xs['right'])

        c_specs = [
            ('code', 2, 0, 'text', _('Code'), None, cell_style),
            ('acc_part', 3, 0, 'text', _('(Account/Partner) Name'), None, cell_style),
            ('dr', 2, 0, 'text', _('Debit'), None, cell_style_right),
            ('cr', 2, 0, 'text', _('Credit'), None, cell_style_right),
            ('bal', 2, 0, 'text', _('Balance'), None, cell_style_right),
            ('disp', 1, 0, 'text', _('In dispute'), None, cell_style_right),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        return row_position

    def print_header_data(self, ws, _p, data, row_position, xlwt, _xs):
        cell_format = _xs['bold'] + _xs['borders_bottom']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str=report_xls.decimal_format)
        cell_style_currency = xlwt.easyxf(cell_format + _xs['right'], num_format_str='_(%s* #,##0.00_);_(%s* (#,##0.00);_(%s* "-"??_);_(@_)' % (_p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol))

        c_specs = [
            ('code', 2, 0, 'text', _('Total:'), None, cell_style),
            ('acc_part', 3, 0, 'text', None),
            ('dr', 2, 0, 'number', _p.sum_debit(), None, cell_style_decimal),
            ('cr', 2, 0, 'number', _p.sum_credit(), None, cell_style_decimal),
            ('bal', 2, 0, 'number', (_p.sum_debit()-_p.sum_credit()), None, cell_style_currency),
            ('disp', 1, 0, 'number', _p.sum_litige(), None, cell_style_currency),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        return row_position

    def print_row_data(self, ws, _p, data, row_line, row_position, xlwt, _xs):
        cell_format = _xs['borders_bottom']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_bold = xlwt.easyxf(cell_format + _xs['bold'])
        cell_style_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str=report_xls.decimal_format)
        cell_style_bold_decimal = xlwt.easyxf(cell_format + _xs['bold'] + _xs['right'], num_format_str=report_xls.decimal_format)
        cell_style_currency = xlwt.easyxf(cell_format + _xs['right'], num_format_str='_(%s* #,##0.00_);_(%s* (#,##0.00);_(%s* "-"??_);_(@_)' % (_p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol))
        cell_style_bold_currency = xlwt.easyxf(cell_format + _xs['bold'] + _xs['right'], num_format_str='_(%s* #,##0.00_);_(%s* (#,##0.00);_(%s* "-"??_);_(@_)' % (_p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol))

        if row_line['type'] == 1:
            c_specs = [
                ('code', 2, 0, 'text', row_line['ref'], None, cell_style),
                ('none', 1, 0, 'text', None),
                ('acc_part', 2, 0, 'text', row_line['move_name'], None, cell_style),
                ('dr', 2, 0, 'number', row_line['debit'], None, cell_style_decimal),
                ('cr', 2, 0, 'number', row_line['credit'], None, cell_style_decimal),
                ('bal', 2, 0, 'number', row_line['balance'], None, cell_style_currency),
                ('disp', 1, 0, 'number', row_line['enlitige'], None, cell_style_currency),
            ]
        if row_line['type'] == 2:
            c_specs = [
                ('code', 2, 0, 'text', row_line['ref'], None, data['form']['display_detail'] and cell_style_bold or cell_style),
                ('acc_part', 3, 0, 'text', row_line['name'], None, data['form']['display_detail'] and cell_style_bold or cell_style),
                ('dr', 2, 0, 'number', row_line['debit'], None, data['form']['display_detail'] and cell_style_bold_decimal or cell_style_decimal),
                ('cr', 2, 0, 'number', row_line['credit'], None, data['form']['display_detail'] and cell_style_bold_decimal or cell_style_decimal),
                ('bal', 2, 0, 'number', row_line['balance'], None, data['form']['display_detail'] and cell_style_bold_currency or cell_style_currency),
                ('disp', 1, 0, 'number', row_line['enlitige'], None, data['form']['display_detail'] and cell_style_bold_currency or cell_style_currency),
            ]
        if row_line['type'] == 3:
            c_specs = [
                ('code', 2, 0, 'text', row_line['ref'] + u'\n' + row_line['code'], None, cell_style_bold),
                ('acc_part', 3, 0, 'text', row_line['name'], None, cell_style_bold),
                ('dr', 2, 0, 'number', row_line['debit'], None, cell_style_bold_decimal),
                ('cr', 2, 0, 'number', row_line['credit'], None, cell_style_bold_decimal),
                ('bal', 2, 0, 'number', row_line['balance'], None, cell_style_bold_currency),
                ('disp', 1, 0, 'number', row_line['enlitige'], None, cell_style_bold_currency),
            ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        return row_position

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        # Initialisations
        ws = wb.add_sheet('aged.partner.balance')
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        _xs['borders_bottom_black'] = 'borders: bottom thin, bottom_colour black;'
        _xs['borders_bottom'] = 'borders: bottom thin, bottom_colour 22;'

        # Print Title
        row_pos = self.print_title(ws, _p, row_pos, xlwt, _xs)
        
        row_pos = self.print_header_attributes(ws, _p, data, row_pos, xlwt, _xs)

        row_pos = self.print_header_titles(ws, _p, data, row_pos, xlwt, _xs)

        row_pos = self.print_header_data(ws, _p, data, row_pos, xlwt, _xs)
        
        for line in _p.lines():
            row_pos = self.print_row_data(ws, _p, data, line, row_pos, xlwt, _xs)

partner_balance_xls('report.account.report_partnerbalance_xls', 'account.move.line', parser=partner_balance)
