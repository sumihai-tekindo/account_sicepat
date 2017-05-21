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

import xlwt
import logging

from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.report import report_sxw
from openerp.tools.translate import _

from partner_balance import partner_balance

_logger = logging.getLogger(__name__)

class outstanding_followup_detail_xls(report_xls):
	column_sizes = [10, 10, 10, 10, 10, 10, 15, 18, 15, 10, 10]

	def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
		super(outstanding_followup_detail_xls, self).__init__(name, table, rml=rml, parser=parser, header=header, store=store)

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
		cell_style = xlwt.easyxf(_xs['xls_title'] + _xs['center'])
		report_name = 'Laporan Outstanding Piutang Per Staf Collection AR'
		c_specs = [
			('report_name', 11, 0, 'text', report_name),
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
			('name', 6, 0, 'text', data['group_by'] == 'group_partner' and _('Followup / Customer / Fiscal/Period / Account') or _('Followup / Fiscal/Period / Customer / Account'), None, cell_style),
			('date', 1, 0, 'text', _('Date Effective'), None, cell_style),
			('move', 1, 0, 'text', _('Journal Entry'), None, cell_style),
			('date_due', 1, 0, 'text', _('Due Date'), None, cell_style),
			('balance', 2, 0, 'text', _('Balance'), None, cell_style_right),
		]
		row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_position = self.xls_write_row(
			ws, row_position, row_data, row_style=cell_style)
		return row_position

	def print_header_data(self, ws, _p, data, row_position, xlwt, _xs):
		cell_format = _xs['bold'] + _xs['borders_bottom']
		cell_style = xlwt.easyxf(cell_format)
		cell_style_currency = xlwt.easyxf(cell_format + _xs['right'], num_format_str='_(%s* #,##0.00_);_(%s* (#,##0.00);_(%s* "-"??_);_(@_)' % (_p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol))

		c_specs = [
			('name', 6, 0, 'text', _('Total:'), None, cell_style),
			('date', 1, 0, 'text', None),
			('move', 1, 0, 'text', None),
			('date_due', 1, 0, 'text', None),
			('balance', 2, 0, 'number', sum(line['balance'] for line in filter(lambda x: x['level'] == 0, _p.result_receivable_followup())), None, cell_style_currency),
		]
		row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_position = self.xls_write_row(
			ws, row_position, row_data, row_style=cell_style)
		return row_position

	def print_row_data(self, ws, _p, row_line, row_position, xlwt, _xs):
		cell_format = _xs['borders_bottom']
		if not row_line.get('level') > 4:
			cell_format += _xs['bold']
		_xs['indent'] = 'align: inde %s;' % (row_line.get('level', 0))
		cell_style = xlwt.easyxf(cell_format)
		cell_style_indent = xlwt.easyxf(cell_format + _xs['indent'])
		cell_style_currency = xlwt.easyxf(cell_format + _xs['right'], num_format_str='_(%s* #,##0.00_);_(%s* (#,##0.00);_(%s* "-"??_);_(@_)' % (_p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol, _p.res_company.currency_id.symbol))

		if row_line['level'] == 5:
			c_specs = [
				('name', 6, 0, 'text', None),
				('date', 1, 0, 'text', row_line['date'], None, cell_style),
				('move', 1, 0, 'text', row_line['move_name'], None, cell_style),
				('date_due', 1, 0, 'text', row_line['date_maturity'], None, cell_style),
				('balance', 2, 0, 'number', row_line['balance'], None, cell_style_currency),
			]
		else:
			c_specs = [
				('name', 6, 0, 'text', row_line['name'], None, cell_style_indent),
				('date', 1, 0, 'text', None),
				('move', 1, 0, 'text', None),
				('date_due', 1, 0, 'text', None),
				('balance', 2, 0, 'number', row_line['balance'], None, cell_style_currency),
			]
		row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_position = self.xls_write_row(
			ws, row_position, row_data, row_style=cell_style)
		return row_position

	def generate_xls_report(self, _p, _xs, data, objects, wb):

		ws = wb.add_sheet('outstanding.followup.dtl')
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0  # Landscape
		ws.fit_width_to_pages = 1
		row_pos = 0
		ws.header_str = self.xls_headers['standard']
		ws.footer_str = self.xls_footers['standard']
		
		_xs['borders_bottom_black'] = 'borders: bottom thin, bottom_colour black;'
		_xs['borders_bottom'] = 'borders: bottom thin, bottom_colour 22;'

		row_pos = self.print_title(ws, _p, row_pos, xlwt, _xs)

		row_pos = self.print_header_titles(ws, _p, data, row_pos, xlwt, _xs)

		row_pos = self.print_header_data(ws, _p, data, row_pos, xlwt, _xs)

		for line in _p.result_receivable_followup():
			row_pos = self.print_row_data(ws, _p, line, row_pos, xlwt, _xs)

outstanding_followup_detail_xls('report.outstanding.followup.detail.xls', 'account.move.line',
					parser=partner_balance)
