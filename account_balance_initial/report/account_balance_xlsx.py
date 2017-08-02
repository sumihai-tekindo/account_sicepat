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
from .account_balance import account_balance
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class ReportTrialBalanceXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objs):
        objs = objs or self.parser_instance.localcontext['objects']
        _p = AttrDict(self.parser_instance.localcontext)
        worksheet = workbook.add_worksheet('trial.balance')
        worksheet.set_landscape()
        worksheet.set_column('A:A', 7)
        worksheet.set_column('B:B', 7)
        worksheet.set_column('C:C', 7.86)
        worksheet.set_column('D:D', 7.86)
        worksheet.set_column('E:E', 7.86)
        worksheet.set_column('F:F', 7.86)
        worksheet.set_column('G:G', 7.86)
        worksheet.set_column('H:H', 7.86)
        worksheet.set_column('I:I', 7.86)
        worksheet.set_column('J:J', 7.86)
        worksheet.set_column('K:K', 7.86)
        worksheet.set_column('L:L', 7.86)
        worksheet.set_column('M:M', 7.86)
        worksheet.set_column('N:N', 7.86)
        worksheet.set_column('O:O', 7.86)
        worksheet.set_column('P:P', 7.86)
        if data['form'].get('initial_balance'):
            worksheet.set_column('Q:Q', 7.86)
            worksheet.set_column('R:R', 7.86)
            worksheet.set_column('S:S', 7.86)
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
        display_account = ''
        if data['form']['display_account'] == 'all':
            display_account = 'All accounts\''
        if data['form']['display_account'] == 'movement':
            display_account = 'With movements'
        if data['form']['display_account'] == 'not_zero':
            display_account = 'With balance not equal to zero'
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
        if data['form'].get('initial_balance'):
            worksheet.merge_range(0, 0, 0, 18, 'Trial Balance', cell_format_title)
            worksheet.merge_range(1, 0, 1, 18, None, cell_format_title)
            worksheet.merge_range(2, 0, 2, 3, 'Chart of Accounts:', cell_format_bold)
            worksheet.merge_range(2, 4, 2, 7, 'Fiscal Year:', cell_format_bold)
            worksheet.merge_range(2, 8, 2, 12, 'Display Account', cell_format_bold)
            worksheet.merge_range(2, 13, 2, 18, 'Filter By:', cell_format_bold)
            worksheet.merge_range(3, 0, 3, 3, _p.get_account(data), cell_format)
            worksheet.merge_range(3, 4, 3, 7, _p.get_fiscalyear(data), cell_format)
            worksheet.merge_range(3, 8, 3, 12, display_account, cell_format)
            worksheet.merge_range(3, 13, 3, 18, filter_by, cell_format_wrap)
            worksheet.merge_range(4, 0, 4, 18, None, cell_format)
            worksheet.merge_range(7, 0, 7, 18, None, cell_format)
        else:
            worksheet.merge_range(0, 0, 0, 15, 'Trial Balance', cell_format_title)
            worksheet.merge_range(1, 0, 1, 15, None, cell_format_title)
            worksheet.merge_range(2, 0, 2, 3, 'Chart of Accounts:', cell_format_bold)
            worksheet.merge_range(2, 4, 2, 6, 'Fiscal Year:', cell_format_bold)
            worksheet.merge_range(2, 7, 2, 10, 'Display Account', cell_format_bold)
            worksheet.merge_range(2, 11, 2, 15, 'Filter By:', cell_format_bold)
            worksheet.merge_range(3, 0, 3, 3, _p.get_account(data), cell_format)
            worksheet.merge_range(3, 4, 3, 6, _p.get_fiscalyear(data), cell_format)
            worksheet.merge_range(3, 7, 3, 10, display_account, cell_format)
            worksheet.merge_range(3, 11, 3, 15, filter_by, cell_format_wrap)
            worksheet.merge_range(4, 0, 4, 15, None, cell_format)
            worksheet.merge_range(7, 0, 7, 15, None, cell_format)
        worksheet.merge_range(5, 0, 5, 3, 'Target Moves:', cell_format_bold)
        worksheet.merge_range(6, 0, 6, 3, _p.get_target_move(data), cell_format)
        
        worksheet.merge_range(8, 0, 8, 1, 'Code', cell_format_bold)
        worksheet.merge_range(8, 2, 8, 6, 'Account', cell_format_bold)
        if data['form'].get('initial_balance'):
            worksheet.merge_range(8, 7, 8, 9, 'Initial Balance', cell_format_bold)
            worksheet.merge_range(8, 10, 8, 12, 'Debit', cell_format_bold)
            worksheet.merge_range(8, 13, 8, 15, 'Credit', cell_format_bold)
            worksheet.merge_range(8, 16, 8, 18, 'Balance', cell_format_bold)
        else:
            worksheet.merge_range(8, 7, 8, 9, 'Debit', cell_format_bold)
            worksheet.merge_range(8, 10, 8, 12, 'Credit', cell_format_bold)
            worksheet.merge_range(8, 13, 8, 15, 'Balance', cell_format_bold)
        row = 9
        for childrenaccount in _p.lines(data['form']):
            cell_format_bold_indent.set_indent(childrenaccount['level'] - 1)
            cell_format_indent.set_indent(childrenaccount['level'] - 1)
            worksheet.merge_range(row, 0, row, 1, childrenaccount['code'], childrenaccount['type'] == 'view' and cell_format_bold or cell_format)
            worksheet.merge_range(row, 2, row, 6, ' '*(childrenaccount['level'] - 1) + childrenaccount['name'], childrenaccount['type'] == 'view' and cell_format_bold or cell_format)
            if data['form'].get('initial_balance'):
                worksheet.merge_range(row, 7, row, 9, childrenaccount['init_balance'], childrenaccount['type'] == 'view' and cell_format_decimal_bold or cell_format_decimal)
                worksheet.merge_range(row, 10, row, 12, childrenaccount['debit'], childrenaccount['type'] == 'view' and cell_format_decimal_bold or cell_format_decimal)
                worksheet.merge_range(row, 13, row, 15, childrenaccount['credit'], childrenaccount['type'] == 'view' and cell_format_decimal_bold or cell_format_decimal)
                worksheet.merge_range(row, 16, row, 18, childrenaccount['balance'], childrenaccount['type'] == 'view' and cell_format_decimal_bold or cell_format_decimal)
            else:
                worksheet.merge_range(row, 7, row, 9, childrenaccount['debit'], childrenaccount['type'] == 'view' and cell_format_decimal_bold or cell_format_decimal)
                worksheet.merge_range(row, 10, row, 12, childrenaccount['credit'], childrenaccount['type'] == 'view' and cell_format_decimal_bold or cell_format_decimal)
                worksheet.merge_range(row, 13, row, 15, childrenaccount['balance'], childrenaccount['type'] == 'view' and cell_format_decimal_bold or cell_format_decimal)
            row += 1
        
ReportTrialBalanceXlsx('report.account.report_trialbalance_xlsx', 'account.account', parser=account_balance)
