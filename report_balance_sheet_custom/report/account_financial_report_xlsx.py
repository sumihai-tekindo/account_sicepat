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
from .account_common_report import report_account_common_inh
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class ReportAccountCommonXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objs):
        objs = objs or self.parser_instance.localcontext['objects']
        _p = AttrDict(self.parser_instance.localcontext)
        for obj in objs:
            worksheet = workbook.add_worksheet(data['form']['account_report_id'][1])
            worksheet.set_portrait()
            worksheet.set_column('A:A', 7.86)
            worksheet.set_column('B:B', 7.86)
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
            worksheet.merge_range(0, 0, 0, 13, data['form']['account_report_id'][1], cell_format_title)
            worksheet.merge_range(1, 0, 1, 13, None, cell_format_title)
            worksheet.merge_range(2, 0, 2, 3, 'Chart of Accounts:', cell_format_bold)
            worksheet.merge_range(2, 4, 2, 6, 'Fiscal Year:', cell_format_bold)
            worksheet.merge_range(2, 7, 2, 10, 'Filter By:', cell_format_bold)
            worksheet.merge_range(2, 11, 2, 13, 'Target Moves:', cell_format_bold)
            worksheet.merge_range(3, 0, 3, 3, _p.get_account(data), cell_format)
            worksheet.merge_range(3, 4, 3, 6, _p.get_fiscalyear(data), cell_format)
            worksheet.merge_range(3, 7, 3, 10, filter_by, cell_format_wrap)
            worksheet.merge_range(3, 11, 3, 13, _p.get_target_move(data), cell_format)
            worksheet.merge_range(4, 0, 4, 13, None, cell_format)
            
            if data['form']['debit_credit']:
                worksheet.merge_range(5, 0, 5, 4, 'Name', cell_format_bold)
                worksheet.merge_range(5, 5, 5, 7, 'Debit', cell_format_bold_right)
                worksheet.merge_range(5, 8, 5, 10, 'Credit', cell_format_bold_right)
                worksheet.merge_range(5, 11, 5, 13, 'Balance', cell_format_bold_right)
                row = 6
                for a in _p.get_lines(data):
                    if a['level'] != 0:
                        worksheet.merge_range(row, 0, row, 4, '  '*(a.get('level', 0)) + a.get('name'), not a['level'] > 3 and cell_format_bold or cell_format)
                        worksheet.merge_range(row, 5, row, 7, a.get('debit'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                        worksheet.merge_range(row, 8, row, 10, a.get('credit'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                        worksheet.merge_range(row, 11, row, 13, a.get('balance'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                        row += 1
            
            if not data['form']['enable_filter'] and not data['form']['debit_credit']:
                worksheet.merge_range(5, 0, 5, 10, 'Name', cell_format_bold)
                worksheet.merge_range(5, 11, 5, 13, 'Balance', cell_format_bold_right)
                row = 6
                for a in _p.get_lines(data):
                    if a['level'] != 0:
                        worksheet.merge_range(row, 0, row, 10, '  '*(a.get('level', 0)) + a.get('name'), not a['level'] > 3 and cell_format_bold or cell_format)
                        worksheet.merge_range(row, 11, row, 13, a.get('balance'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                        row += 1

            if data['form']['enable_filter'] and not data['form']['debit_credit']:
                if data['form']['with_difference'] or data['form']['with_total']:
                    text_str = ''
                    if data['form']['with_difference']:
                        text_str = 'Diff.'
                    elif data['form']['with_total']:
                        text_str = 'Total.'
                    worksheet.merge_range(5, 0, 5, 4, 'Name', cell_format_bold)
                    worksheet.merge_range(5, 5, 5, 7, 'Balance', cell_format_bold_right)
                    worksheet.merge_range(5, 8, 5, 10, data['form']['label_filter'], cell_format_bold_right)
                    worksheet.merge_range(5, 11, 5, 13, text_str, cell_format_bold_right)
                else:
                    worksheet.merge_range(5, 0, 5, 7, 'Name', cell_format_bold)
                    worksheet.merge_range(5, 8, 5, 10, 'Balance', cell_format_bold_right)
                    worksheet.merge_range(5, 11, 5, 13, data['form']['label_filter'], cell_format_bold_right)
                row = 6
                for a in _p.get_lines(data):
                    if a['level'] != 0:
                        if data['form']['with_difference'] or data['form']['with_total']:
                            worksheet.merge_range(row, 0, row, 4, '  '*(a.get('level', 0)) + a.get('name'), not a['level'] > 3 and cell_format_bold or cell_format)
                            worksheet.merge_range(row, 5, row, 7, a.get('balance'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                            worksheet.merge_range(row, 8, row, 10, a.get('balance_cmp'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                            if data['form']['with_difference']:
                                worksheet.merge_range(row, 11, row, 13, a.get('balance_diff'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                            elif data['form']['with_difference']:
                                worksheet.merge_range(row, 11, row, 13, a.get('balance_total'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                        else:
                            worksheet.merge_range(row, 0, row, 7, ' '*(a.get('level', 0)) + a.get('name'), not a['level'] > 3 and cell_format_bold or cell_format)
                            worksheet.merge_range(row, 8, row, 10, a.get('balance'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                            worksheet.merge_range(row, 11, row, 13, a.get('balance_cmp'), not a['level'] > 3 and cell_format_decimal_bold or cell_format_decimal)
                        row += 1
            
        
ReportAccountCommonXlsx('report.account.report_financial_xlsx', 'account.financial.report', parser=report_account_common_inh)
