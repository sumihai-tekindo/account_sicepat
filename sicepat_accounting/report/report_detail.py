# -*- encoding: utf-8 -*-
##############################################################################
#
#	OpenERP, Open Source Management Solution
#
#	Copyright (c) 2013 PT. SUMIHAI TEKNOLOGI INDONESIA. All rights reserved.
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from partner_balance import partner_balance
from datetime import datetime
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class revenue_package(ReportXlsx):

	def generate_xlsx_report(self, workbook, data, objs):
		worksheet = workbook.add_worksheet('daily.piutang.dtl')
		worksheet.set_landscape()
		worksheet.set_column('A:A', 50)
		worksheet.set_column('B:B', 15)
		worksheet.set_column('C:C', 20)
		worksheet.set_column('D:D', 15)
		worksheet.set_column('E:E', 20)
		worksheet.set_column('F:F', 20)
		worksheet.set_column('G:G', 20)
		worksheet.set_column('H:H', 20)
		worksheet.set_column('I:I', 20)
		worksheet.set_column('J:J', 20)

		cell_format_title = workbook.add_format({'bold': 1})
		cell_format_bold = workbook.add_format({'bold': 1})
		cell_format_bold_center = workbook.add_format({'bold': 1})
		cell_format_bold_right = workbook.add_format({'bold': 1})
		cell_format_decimal = workbook.add_format({'num_format': '_(#,##0.00_);(#,##0.00)'})
		cell_format_decimal_bold = workbook.add_format({'bold': 1})
		cell_format_date = workbook.add_format()
		cell_format = workbook.add_format()
		cell_format_title.set_font_size(16)
		cell_format_bold_center.set_align('center')
		cell_format_bold_right.set_align('right')
		worksheet.merge_range(0, 0, 0, 5, 'LAPORAN PIUTANG PER HARI DETAIL', cell_format_bold_center)

		worksheet.merge_range(1, 0, 1, 5, None, cell_format_title)
		worksheet.write(2, 0, 'Customer / Fiscal/Period / Account', cell_format_bold)
		worksheet.write(2, 1, 'Date Effective', cell_format_bold)
		worksheet.write(2, 2, 'Journal Entry', cell_format_bold)
		worksheet.write(2, 3, 'Due Date', cell_format_bold)
		worksheet.write(2, 4, 'Balance', cell_format_bold)
		
		_p = AttrDict(self.parser_instance.localcontext)
		row = 4
		for line in _p.result_receivable():
			# if row < 30 :
				if line['level'] == 0 :
					worksheet.write(3, 0, 'Total', cell_format_bold)
					worksheet.write(3, 1,'', cell_format_bold)
					worksheet.write(3, 2,'', cell_format_bold)
					worksheet.write(3, 3,'', cell_format_bold)
					worksheet.write(3, 4, line['balance'], cell_format_decimal)

					worksheet.write(row, 0,line['name'], cell_format_bold)
					worksheet.write(row, 1,'', cell_format)
					worksheet.write(row, 2,'', cell_format)
					worksheet.write(row, 3,'', cell_format)
					worksheet.write(row, 4, line['balance'], cell_format_decimal)
				elif line['level'] == 1 :
					worksheet.write(row, 0,line['name'], cell_format_bold)
					worksheet.write(row, 1,'', cell_format)
					worksheet.write(row, 2,'', cell_format)
					worksheet.write(row, 3,'', cell_format)
					worksheet.write(row, 4, line['balance'], cell_format_decimal)
				elif line['level'] == 2 :
					worksheet.write(row, 0,line['name'], cell_format_bold)
					worksheet.write(row, 1,'', cell_format)
					worksheet.write(row, 2,'', cell_format)
					worksheet.write(row, 3,'', cell_format)
					worksheet.write(row, 4, line['balance'], cell_format_decimal)
				elif line['level'] == 3 :
					worksheet.write(row, 0,line['name'], cell_format_bold)
					worksheet.write(row, 1,'', cell_format)
					worksheet.write(row, 2,'', cell_format)
					worksheet.write(row, 3,'', cell_format)
					worksheet.write(row, 4, line['balance'], cell_format_decimal)
				elif line['level'] == 4 :
					worksheet.write(row, 0,'', cell_format_bold)
					worksheet.write(row, 1,line['date'], cell_format_date)
					worksheet.write(row, 2,line['move_name'], cell_format)
					worksheet.write(row, 3,line['date_maturity'], cell_format_date)
					worksheet.write(row, 4, line['balance'], cell_format_decimal)

				row += 1

revenue_package('report.revenue.package3', 'account.move.line',parser=partner_balance)
