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
from datetime import datetime
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from .account_journal import journal_print
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class AccountPrintJournalXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objs):
        _p = AttrDict(self.parser_instance.localcontext)
        for rec in _p.get_printjournal():
            worksheet = workbook.add_worksheet(rec['key'].replace('/','_'))
            worksheet.set_landscape()
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 12)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 25)
            worksheet.set_column('E:E', 55)
            worksheet.set_column('F:F', 18)
            worksheet.set_column('G:G', 18)
            cell_format_title = workbook.add_format({'bold': 1})
            cell_format_bold = workbook.add_format({'bold': 1})
            cell_format_bold_center = workbook.add_format({'bold': 1})
            cell_format_bold_right = workbook.add_format({'bold': 1})
            cell_format_decimal = workbook.add_format()
            cell_format_decimal_bold = workbook.add_format({'bold': 1})
            cell_format_date = workbook.add_format()
            cell_format = workbook.add_format()
            cell_format_title.set_font_size(16)
            cell_format_bold_center.set_align('center')
            cell_format_bold_right.set_align('right')
            cell_format_decimal.set_num_format('#,##0.00')
            cell_format_decimal_bold.set_num_format('#,##0.00')
            cell_format_date.set_num_format('dd-mmm-yyyy')
            worksheet.merge_range(0, 0, 0, 1, 'Journal', cell_format_title)
            worksheet.merge_range(1, 0, 1, 6, None, cell_format_title)
            worksheet.merge_range(2, 0, 2, 1, 'Chart of Accounts:', cell_format_bold)
            worksheet.merge_range(2, 2, 2, 3, 'Fiscal Year:', cell_format_bold)
            worksheet.write(2, 4, 'Journal:', cell_format_bold)
            worksheet.merge_range(2, 5, 2, 6, 'Period:', cell_format_bold)
            worksheet.merge_range(3, 0, 3, 1, _p.get_account(data), cell_format)
            worksheet.merge_range(3, 2, 3, 3, _p.get_fiscalyear(data), cell_format)
            worksheet.write(3, 4, rec['journal_name'], cell_format)
            worksheet.merge_range(3, 5, 3, 6, rec['period_name'], cell_format)
            worksheet.merge_range(4, 0, 4, 6, None, cell_format)
            worksheet.merge_range(5, 0, 5, 1, 'Entries Sorted By:', cell_format_bold)
            worksheet.merge_range(5, 2, 5, 3, 'Target Moves:', cell_format_bold)
            if data['form'].get('sort_selection') == 'l.date':
                worksheet.merge_range(6, 0, 6, 1, 'Date', cell_format)
            if data['form'].get('sort_selection') == 'am.name':
                worksheet.merge_range(6, 0, 6, 1, 'Journal Entry Number', cell_format)
            worksheet.merge_range(6, 2, 6, 3, _p.get_target_move(data), cell_format)
            worksheet.merge_range(7, 0, 7, 6, None, cell_format)
            worksheet.write(8, 0, 'Move', cell_format_bold_center)
            worksheet.write(8, 1, 'Date', cell_format_bold_center)
            worksheet.write(8, 2, 'Account', cell_format_bold_center)
            worksheet.write(8, 3, 'Partner', cell_format_bold_center)
            worksheet.write(8, 4, 'Label', cell_format_bold_center)
            worksheet.write(8, 5, 'Debit', cell_format_bold_center)
            worksheet.write(8, 6, 'Credit', cell_format_bold_center)
            if _p.display_currency(data):
                worksheet.write(8, 7, 'Currency', cell_format_bold)
            row = 9
            for line in rec['lines']:
                worksheet.write(row, 0, line.move_id.name != '/' and line.move_id.name or ('*'+str(line.move_id.id)), cell_format)
                worksheet.write(row, 1, line.date, cell_format_date)
                worksheet.write(row, 2, line.account_id.code, cell_format)
                worksheet.write(row, 3, line.partner_id and line.partner_id.name or None, cell_format)
                worksheet.write(row, 4, line.name, cell_format)
                worksheet.write(row, 5, line.debit, cell_format_decimal)
                worksheet.write(row, 6, line.credit, cell_format_decimal)
                if _p.display_currency(data):
                    worksheet.write(row, 7, line.amount_currency or None, cell_format_decimal)
                row += 1
            
            worksheet.write(row, 4, 'Total', cell_format_bold_right)
            worksheet.write(row, 5, rec['debit'], cell_format_decimal_bold)
            worksheet.write(row, 6, rec['credit'], cell_format_decimal_bold)
            
AccountPrintJournalXlsx('report.account.report_printjournal_xlsx', 'account.move.line', parser=journal_print)
