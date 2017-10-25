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

# import xlsxwriter
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from .account_general_ledger import general_ledger
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class ReportGeneralLedgerXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objs):
        objs = objs or self.parser_instance.localcontext['objects']
        _p = AttrDict(self.parser_instance.localcontext)
        for obj in objs:
            worksheet = workbook.add_worksheet(_p.get_children_accounts(obj)[0]['code'])
            worksheet.set_landscape()
            worksheet.set_column('A:A', 7)
            worksheet.set_column('B:B', 7)
            worksheet.set_column('C:C', 7.86)
            worksheet.set_column('D:D', 7.86)
            worksheet.set_column('E:E', 7.86)
            worksheet.set_column('F:F', 7)
            worksheet.set_column('G:G', 7.86)
            worksheet.set_column('H:H', 7)
            worksheet.set_column('I:I', 7.86)
            worksheet.set_column('J:J', 7.86)
            worksheet.set_column('K:K', 7.86)
            worksheet.set_column('L:L', 7.86)
            worksheet.set_column('M:M', 7)
            worksheet.set_column('N:N', 7)
            worksheet.set_column('O:O', 7.86)
            worksheet.set_column('P:P', 7.86)
            worksheet.set_column('Q:Q', 7.86)
            worksheet.set_column('R:R', 7.86)
            worksheet.set_column('S:S', 7.86)
            worksheet.set_column('T:T', 7.86)
            worksheet.set_column('U:U', 7.86)
            worksheet.set_column('V:V', 7.86)
            cell_format_title = workbook.add_format({'bold': 1})
            cell_format_bold = workbook.add_format({'bold': 1})
            cell_format_bold_center = workbook.add_format({'bold': 1})
            cell_format_bold_right = workbook.add_format({'bold': 1})
            cell_format_bold_indent = workbook.add_format({'bold': 1})
            cell_format_decimal_bold = workbook.add_format({'bold': 1})
            cell_format = workbook.add_format()
            cell_format_indent = workbook.add_format()
            cell_format_wrap = workbook.add_format()
            cell_format_decimal = workbook.add_format()
            cell_format_date = workbook.add_format()
            cell_format_title.set_font_size(16)
            cell_format_bold_center.set_align('center')
            cell_format_bold_right.set_align('right')
            cell_format_decimal_bold.set_num_format('#,##0.00')
            cell_format_wrap.set_text_wrap()
            cell_format_decimal.set_num_format('#,##0.00')
            cell_format_date.set_num_format('dd-mmm-yyyy')
            worksheet.merge_range(0, 0, 0, 21, 'General ledger', cell_format_title)
            worksheet.merge_range(1, 0, 1, 21, None, cell_format_title)
            worksheet.merge_range(2, 0, 2, 4, 'Chart of Accounts:', cell_format_bold)
            worksheet.merge_range(2, 5, 2, 9, 'Fiscal Year:', cell_format_bold)
            worksheet.merge_range(2, 10, 2, 15, 'Journals:', cell_format_bold)
            worksheet.merge_range(2, 16, 2, 21, 'Display Account', cell_format_bold)
            worksheet.merge_range(3, 0, 3, 4, _p.get_account(data), cell_format)
            worksheet.merge_range(3, 5, 3, 9, _p.get_fiscalyear(data), cell_format)
            worksheet.merge_range(3, 10, 3, 15, ', '.join([ lt or '' for lt in _p.get_journal(data) ]), cell_format_wrap)
            display_account = ''
            if data['form']['display_account'] == 'all':
                display_account = 'All accounts\''
            if data['form']['display_account'] == 'movement':
                display_account = 'With movements'
            if data['form']['display_account'] == 'not_zero':
                display_account = 'With balance not equal to zero'
            worksheet.merge_range(3, 16, 3, 21, display_account, cell_format)
            worksheet.merge_range(4, 0, 4, 21, None, cell_format)
            
            worksheet.merge_range(5, 0, 5, 4, 'Filter By:', cell_format_bold)
            worksheet.merge_range(5, 5, 5, 9, 'Sorted By:', cell_format_bold)
            worksheet.merge_range(5, 10, 5, 15, 'Target Moves:', cell_format_bold)
            filter_by = ''
            if data['form']['filter'] == 'filter_no':
                filter_by = 'Not filtered'
            if data['form']['filter'] == 'filter_period':
                filter_by = 'Filtered by period\n\n'
                filter_by += 'Start Period: %s\n' % _p.get_start_period(data)
                filter_by += 'End Period: %s' % _p.get_end_period(data)
            if data['form']['filter'] == 'filter_date':
                filter_by = 'Filtered by date\n\n'
                filter_by += 'Date from: %s\n' % _p.formatLang(_p.get_start_date(data), date=True)
                filter_by += 'Date to: %s' % _p.formatLang(_p.get_end_date(data), date=True)
            worksheet.merge_range(6, 0, 6, 4, filter_by, cell_format_wrap)
            worksheet.merge_range(6, 5, 6, 9, _p.get_sortby(data), cell_format)
            worksheet.merge_range(6, 10, 6, 15, _p.get_target_move(data), cell_format)
            worksheet.merge_range(7, 0, 7, 21, None, cell_format)
            
            worksheet.merge_range(8, 0, 8, 1, 'Date', cell_format_bold)
            worksheet.write(8, 2, 'JRNL', cell_format_bold)
            worksheet.merge_range(8, 3, 8, 4, 'Partner', cell_format_bold)
            worksheet.merge_range(8, 5, 8, 6, 'Ref', cell_format_bold)
            worksheet.merge_range(8, 7, 8, 8, 'Move', cell_format_bold)
            worksheet.merge_range(8, 9, 8, 14, 'Entry Label', cell_format_bold)
            worksheet.merge_range(8, 15, 8, 16, 'Counterpart', cell_format_bold)
            worksheet.merge_range(8, 17, 8, 18, 'Analytic Account', cell_format_bold)
            worksheet.merge_range(8, 19, 8, 20, 'Debit', cell_format_bold)
            worksheet.merge_range(8, 21, 8, 22, 'Credit', cell_format_bold)
            worksheet.merge_range(8, 23, 8, 24, 'Balance', cell_format_bold)
            if data['form']['amount_currency']:
                worksheet.merge_range(8, 25, 8, 26, 'Currency', cell_format_bold)
            row = 9
            for childrenaccount in _p.get_children_accounts(obj):
                cell_format_bold_indent.set_indent(childrenaccount['level'] - 1)
                worksheet.merge_range(row, 0, row, 13, childrenaccount['code'] + ' ' + childrenaccount['name'], cell_format_bold_indent)
                worksheet.merge_range(row, 19, row, 20, _p.sum_debit_account(childrenaccount), cell_format_decimal_bold)
                worksheet.merge_range(row, 21, row, 22, _p.sum_credit_account(childrenaccount), cell_format_decimal_bold)
                worksheet.merge_range(row, 23, row, 24, _p.sum_balance_account(childrenaccount), cell_format_decimal_bold)
                if data['form']['amount_currency']:
                    worksheet.merge_range(row, 25, row, 26, _p.sum_currency_amount_account(childrenaccount), cell_format_decimal)
                row += 1
                for line in _p.lines(childrenaccount):
                    worksheet.merge_range(row, 0, row, 1, line['ldate'], cell_format_date)
                    worksheet.write(row, 2, line['lcode'], cell_format)
                    worksheet.merge_range(row, 3, row, 4, line['partner_name'], cell_format)
                    worksheet.merge_range(row, 5, row, 6, line['lref'], cell_format)
                    worksheet.merge_range(row, 7, row, 8, line['move'], cell_format)
                    worksheet.merge_range(row, 9, row, 14, line['lname'], cell_format)
                    worksheet.merge_range(row, 15, row, 16, line['line_corresp'].replace(',',', '), cell_format)
                    worksheet.merge_range(row, 17, row, 18, line['analytic_account'], cell_format)
                    worksheet.merge_range(row, 19, row, 20, line['debit'], cell_format_decimal)
                    worksheet.merge_range(row, 21, row, 22, line['credit'], cell_format_decimal)
                    worksheet.merge_range(row, 23, row, 24, line['progress'], cell_format_decimal)
                    if data['form']['amount_currency']:
                        worksheet.merge_range(row, 25, row, 26, line['amount_currency'] > 0.0 and line['amount_currency'] or '', cell_format_decimal)
                    row += 1
        
ReportGeneralLedgerXlsx('report.account.report_generalledger_xlsx', 'account.account', parser=general_ledger)
