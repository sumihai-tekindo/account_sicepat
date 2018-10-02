# -*- coding: utf-8 -*-
##############################################################################
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

import pytz
import logging
import xlwt
from datetime import datetime
from openerp.addons.report_xls.report_xls import report_xls
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _
from openerp.osv import fields, osv
_logger = logging.getLogger(__name__)

class report_invoice_paid_xls(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(report_invoice_paid_xls, self).__init__(cr, uid, name, context=context)

class invoice_paid_xls(report_xls):
	def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
		super(invoice_paid_xls, self).__init__(name, table, rml=rml, parser=parser, header=header, store=store)

	def generate_xls_report(self, _p, _xs, data, objects, wb):
		ws = wb.add_sheet('paid.invoice')
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
		company = _p.company.name
		c_specs = [
			('company', 1, 0, 'text', company),
		]
		row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

		# Sub Title
		cell_style = xlwt.easyxf(_xs['xls_title'])
		report_name = 'Laporan Pengajuan Pengeluaran Bank'
		c_specs = [
			('report_name', 1, 0, 'text', report_name),
		]
		row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

		# print datetime
		cell_style = xlwt.easyxf(_xs['bold'])
		today = datetime.utcnow()
		context_today = None
		tz_name = _p.user.tz
		if tz_name:
			try:
				today_utc = pytz.timezone('UTC').localize(today, is_dst=False)  # UTC = no DST
				context_today = today_utc.astimezone(pytz.timezone(tz_name))
			except Exception:
				_logger.debug("failed to compute context/client-specific today date, using UTC value for `today`",
					exc_info=True)
		datetime_print = (context_today or today).strftime('%d-%B-%Y %H:%M:%S')
		c_specs = [
			('report_name', 1, 0, 'text', datetime_print),
		]
		row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

		# write empty row to define column sizes
		c_sizes = [12,20,15,30,18,65,15,15]
		c_specs = [
			('empty%s' % i, 1, c_sizes[i], 'text', None) for i in range(0, len(c_sizes))
		]
		row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_pos = self.xls_write_row(ws, row_pos, row_data, set_column_size=True)

		# Column Header Row
		cell_format = _xs['borders_all']
		c_hdr_cell_style_center = xlwt.easyxf(cell_format + _xs['fill'] + _xs['bold'] + _xs['center'])
		c_specs = [
			('date_invoice', 1, 0, 'text', _('Invoice Date'), None, c_hdr_cell_style_center),
			('payment_date', 1, 0, 'text', _('Payment Date'), None, c_hdr_cell_style_center),
			('bank_name', 1, 0, 'text', _('Bank'), None, c_hdr_cell_style_center),
			('bank_account', 1, 0, 'text', _('Account No'), None, c_hdr_cell_style_center),
			('bank_owner', 1, 0, 'text', _('Beneficiary Name'), None, c_hdr_cell_style_center),
			('number_invoice', 1, 0, 'text', _('Invoice No'), None, c_hdr_cell_style_center),
			('line_product_id', 1, 0, 'text', _('Product Name'), None, c_hdr_cell_style_center),
			('line_name', 1, 0, 'text', _('Description'), None, c_hdr_cell_style_center),
			('line_account_id', 1, 0, 'text', _('Chart of Account'), None, c_hdr_cell_style_center),
			('line_account_analytic_id', 1, 0, 'text', _('Account Analytic'), None, c_hdr_cell_style_center),
			('line_quantity', 1, 0, 'text', _('Quantity'), None, c_hdr_cell_style_center),
			('line_price_unit', 1, 0, 'text', _('Unit Price'), None, c_hdr_cell_style_center),
			('line_discount', 1, 0, 'text', _('Discount'), None, c_hdr_cell_style_center),
			('line_amount', 1, 0, 'text', _('Amount'), None, c_hdr_cell_style_center),
			('total', 1, 0, 'text', _('Total'), None, c_hdr_cell_style_center),
		]
		c_hdr_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_pos = self.xls_write_row(ws, row_pos, c_hdr_data, row_style=c_hdr_cell_style_center)

		# Column Line Rows
		c_line_cell_style = xlwt.easyxf(cell_format)
		c_line_cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
		c_line_cell_style_date = xlwt.easyxf(cell_format + _xs['right'], num_format_str='DD-MMM-YYYY')
		c_line_cell_style_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str=report_xls.decimal_format)
	
		for inv in objects:
			line_row = 0
			for line in inv.invoice_line:     
			   
				if inv.payment_date == False :
					raise osv.except_osv(_('Warning !'), _('Please select data with status Paid.'))
				c_specs = [
					('date_invoice', 1, 0, 'text', None),
					('payment_date', 1, 0, 'text', None),
					('bank_name', 1, 0, 'text', None),
					('bank_account', 1, 0, 'text', None),
					('bank_owner', 1, 0, 'text', None),
					('number_invoice', 1, 0, 'text', None),
					('line_product_id', 1, 0, 'text', ('[' + line.product_id.default_code +']' + ' ' + line.product_id.name_template), None, c_line_cell_style),
					('line_name', 1, 0, 'text', line.name, None, c_line_cell_style),
					('line_account_id', 1, 0, 'text', ('[' + line.account_id.code +']' + ' ' + line.account_id.name), None, c_line_cell_style),
					# ('line_account_analytic_id', 1, 0, 'text', (line.account_analytic_id.parent_id.parent_id.name +' /' + line.account_analytic_id.parent_id.name +'/'+line.account_analytic_id.name), None, c_line_cell_style),
					('line_account_analytic_id', 1, 0, 'text', line.account_analytic_id.name, None, c_line_cell_style),
					('line_quantity', 1, 0, 'number', line.quantity, None, c_line_cell_style_decimal),
					('line_price_unit', 1, 0, 'number', line.price_unit, None, c_line_cell_style_decimal),
					('line_discount', 1, 0, 'number', (line.discount * line.price_unit)/ 100, None, c_line_cell_style_decimal),
					('line_amount', 1, 0, 'number', line.price_subtotal, None, c_line_cell_style_decimal),
					('total', 1, 0, 'text', None),
				]
				
				if line_row == 0:
					c_specs = [
						inv.payment_date and
						('date_invoice', 1, 0, 'date', datetime.strptime(inv.date_invoice, DF), None, c_line_cell_style_date) or
						('date_invoice', 1, 0, 'text', '-', None, c_line_cell_style_center),
						('payment_date', 1, 0, 'date', datetime.strptime(inv.payment_date, DF), None, c_line_cell_style_date) or
						('payment_date', 1, 0, 'text', '-', None, c_line_cell_style_center),
						('bank_name', 1, 0, 'text', inv.partner_bank_id.bank_name, None, c_line_cell_style),
						('bank_account', 1, 0, 'text', inv.partner_bank_id.acc_number, None, c_line_cell_style),
						('bank_owner', 1, 0, 'text', inv.partner_bank_id.owner_name, None, c_line_cell_style),
						('number_invoice', 1, 0, 'text', inv.number or inv.internal_number, None, c_line_cell_style),
						('line_product_id', 1, 0, 'text', ('['+line.product_id.default_code +']' + ' ' + line.product_id.name_template), None, c_line_cell_style), 
						('line_name', 1, 0, 'text', line.name, None, c_line_cell_style),
						('line_account_id', 1, 0, 'text', ('[' + line.account_id.code +']' + ' ' + line.account_id.name), None, c_line_cell_style),
						# ('line_account_analytic_id', 1, 0, 'text', (line.account_analytic_id.parent_id.parent_id.name +' / '+ line.account_analytic_id.parent_id.name +' / ' + line.account_analytic_id.name), None, c_line_cell_style) or
						# ('line_account_analytic_id', 1, 0, 'text', '-', None, c_line_cell_style_center),
						('line_account_analytic_id', 1, 0, 'text', line.account_analytic_id.name, None, c_line_cell_style),
						('line_quantity', 1, 0, 'number', line.quantity, None, c_line_cell_style_decimal),
						('line_price_unit', 1, 0, 'number', line.price_unit, None, c_line_cell_style_decimal),
						('line_discount', 1, 0, 'number', (line.discount * line.price_unit)/ 100, None, c_line_cell_style_decimal),
						('line_amount', 1, 0, 'number', line.price_subtotal, None, c_line_cell_style_decimal),
						('total', 1, 0, 'number', inv.amount_total, None, c_line_cell_style_decimal),
					]
				row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
				row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_line_cell_style)
				line_row += 1
			for tax in inv.tax_line:
				c_specs = [
					('date_invoice', 1, 0, 'text', None),
					('payment_date', 1, 0, 'text', None),
					('bank_name', 1, 0, 'text', None),
					('bank_account', 1, 0, 'text', None),
					('bank_owner', 1, 0, 'text', None),
					('number_invoice', 1, 0, 'text', None),
					('line_product_id', 1, 0, 'text', None),
					('line_name', 1, 0, 'text', tax.name, None, c_line_cell_style),
					('line_account_id', 1, 0, 'text', ('[' + tax.account_id.code +']' + ' ' + tax.account_id.name), None, c_line_cell_style),
					('line_account_analytic_id', 1, 0, 'text',tax.account_analytic_id.name, None, c_line_cell_style),
					('line_quantity', 1, 0, 'text', None),
					('line_price_unit', 1, 0, 'text', None),
					('line_discount', 1, 0, 'text', None),
					('line_amount', 1, 0, 'number', tax.amount, None, c_line_cell_style_decimal),
					('total', 1, 0, 'text', None),
				]
				row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
				row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=c_line_cell_style)
				
invoice_paid_xls('report.invoice.paid.report.xls', 'account.invoice', parser=report_invoice_paid_xls)