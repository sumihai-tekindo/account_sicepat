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
from .account_aged_partner_balance import aged_trial_report
# from openerp.addons.account.report.account_aged_partner_balance import aged_trial_report
from openerp.tools.translate import _

class aged_trial_report_xls(report_xls):
    column_sizes = [25, 20, 20, 20, 20, 20, 20, 20]
    
    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(aged_trial_report_xls, self).__init__(name, table, rml=rml, parser=parser, header=header, store=store)
        
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
        report_name = 'Aged Trial Balance'
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        
        row_position = self.print_empty_row(ws, row_position)
        return row_position

    def print_header_attributes(self, ws, _p, data, row_position, xlwt, _xs):
        cell_format = _xs['bold']
        cell_style = xlwt.easyxf(cell_format)
        c_specs = [
            ('coa', 2, 0, 'text', _('Chart of Accounts:')),
            ('fy', 2, 0, 'text', _('Fiscal Year:')),
            ('ds', 2, 0, 'text', _('Start Date:')),
            ('pl', 2, 0, 'text', _('Period Length (days)')),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        
        c_specs = [
            ('coa', 2, 0, 'text', _p.get_account(data)),
            ('fy', 2, 0, 'text', _p.get_fiscalyear(data)),
            ('ds', 2, 0, 'text', _p.formatLang(data['form']['date_from'], date=True)),
            ('pl', 2, 0, 'text', str(data['form']['period_length'])),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data)
        
        row_position = self.print_empty_row(ws, row_position)
        c_specs = [
            ('partner', 2, 0, 'text', _('Partner\'s:')),
            ('ad', 2, 0, 'text', _('Analysis Direction:')),
            ('tm', 2, 0, 'text', _('Target Moves:')),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        
        partners = _('')
        if data['form']['result_selection'] == 'customer': partners = _('Receivable Accounts')
        if data['form']['result_selection'] == 'supplier': partners = _('Payable Accounts')
        if data['form']['result_selection'] == 'customer_supplier': partners = _('Receivable and Payable Accounts')
        c_specs = [
            ('partner', 2, 0, 'text', partners),
            ('ad', 2, 0, 'text', data['form']['direction_selection']),
            ('tm', 2, 0, 'text', _p.get_target_move(data)),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data)
        
        row_position = self.print_empty_row(ws, row_position)
        return row_position

    def print_header_titles(self, ws, _p, data, row_position, xlwt, _xs):
        cell_format = _xs['bold']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_right = xlwt.easyxf(cell_format + _xs['right'])

        due_notdue = _('')
        if data['form']['direction_selection'] == 'future': due_notdue = _('Due') 
        if data['form']['direction_selection'] != 'future': due_notdue = _('Not due')
        c_specs = [
            ('partner', 1, 0, 'text', _('Partners'), None, cell_style),
            ('due_notdue', 1, 0, 'text', due_notdue, None, cell_style_right),
            ('4', 1, 0, 'text', data['form']['4']['name'], None, cell_style_right),
            ('3', 1, 0, 'text', data['form']['3']['name'], None, cell_style_right),
            ('2', 1, 0, 'text', data['form']['2']['name'], None, cell_style_right),
            ('1', 1, 0, 'text', data['form']['1']['name'], None, cell_style_right),
            ('0', 1, 0, 'text', data['form']['0']['name'], None, cell_style_right),
            ('total', 1, 0, 'text', _('Total'), None, cell_style_right),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        return row_position

    def print_header_data(self, ws, _p, data, row_position, xlwt, _xs):
        _xs['borders_top_black'] = 'borders: top thin, top_colour black;'
        _xs['borders_bottom_black'] = 'borders: bottom thin, bottom_colour black;'
        cell_format = _xs['bold'] + _xs['borders_top_black'] + _xs['borders_bottom_black']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_currency = xlwt.easyxf(cell_format + _xs['right'], num_format_str='_(%s* #,##0.00_);_(%s* (#,##0.00);_(%s* "-"??_);_(@_)' % (_p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol))

        c_specs = [
            ('partner_total', 1, 0, 'text', _('Account Total'), None, cell_style),
            ('due_notdue_total', 1, 0, 'number', _p.get_direction(6), None, cell_style_currency),
            ('4_total', 1, 0, 'number', _p.get_for_period(4), None, cell_style_currency),
            ('3_total', 1, 0, 'number', _p.get_for_period(3), None, cell_style_currency),
            ('2_total', 1, 0, 'number', _p.get_for_period(2), None, cell_style_currency),
            ('1_total', 1, 0, 'number', _p.get_for_period(1), None, cell_style_currency),
            ('0_total', 1, 0, 'number', _p.get_for_period(0), None, cell_style_currency),
            ('total_total', 1, 0, 'number', _p.get_for_period(5), None, cell_style_currency),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            ws, row_position, row_data, row_style=cell_style)
        return row_position

    def print_row_data(self, ws, _p, row_line, row_position, xlwt, _xs):
        _xs['borders_bottom'] = 'borders: bottom thin, bottom_colour 22;'
        cell_format = _xs['borders_bottom']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_currency = xlwt.easyxf(cell_format + _xs['right'], num_format_str='_(%s* #,##0.00_);_(%s* (#,##0.00);_(%s* "-"??_);_(@_)' % (_p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol))

        c_specs = [
            ('partner', 1, 0, 'text', row_line['name'], None, cell_style),
            ('due_notdue', 1, 0, 'number', row_line['direction'], None, cell_style_currency),
            ('4', 1, 0, 'number', row_line['4'], None, cell_style_currency),
            ('3', 1, 0, 'number', row_line['3'], None, cell_style_currency),
            ('2', 1, 0, 'number', row_line['2'], None, cell_style_currency),
            ('1', 1, 0, 'number', row_line['1'], None, cell_style_currency),
            ('0', 1, 0, 'number', row_line['0'], None, cell_style_currency),
            ('total', 1, 0, 'number', row_line['total'], None, cell_style_currency),
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

        # Print Title
        row_pos = self.print_title(ws, _p, row_pos, xlwt, _xs)
        
        row_pos = self.print_header_attributes(ws, _p, data, row_pos, xlwt, _xs)

        row_pos = self.print_header_titles(ws, _p, data, row_pos, xlwt, _xs)

        if _p.get_lines(data['form']) or _p.get_lines_with_out_partner(data['form']):
            row_pos = self.print_header_data(ws, _p, data, row_pos, xlwt, _xs)
        
        for partner in _p.get_lines(data['form']):
            row_pos = self.print_row_data(ws, _p, partner, row_pos, xlwt, _xs)

        for not_partner in _p.get_lines_with_out_partner(data['form']):
            row_pos = self.print_row_data(ws, _p, not_partner, row_pos, xlwt, _xs)

aged_trial_report_xls('report.account.report_agedpartnerbalance_xls', 'account.move.line', parser=aged_trial_report)
