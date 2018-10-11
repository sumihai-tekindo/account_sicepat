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

# import xlwt
import xlsxwriter
# from xlsxwriter import Formula as fm
from datetime import datetime
from openerp.osv import orm
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
# from openerp.addons.report_xls.utils import rowcol_to_cell, _render

import time
from openerp.report import report_sxw
from openerp.tools.translate import translate
import logging

# from .nov_account_journal import nov_journal_print
from openerp.tools.translate import _
# from partner_balance import partner_balance
import logging
_logger = logging.getLogger(__name__)
from openerp import fields

from openerp.addons.customer_bill_mail.reports.bill_monthly import report_bill_monthly_parser


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class partner_bill_summary_xls(ReportXlsx):

	def __init__(self, name, table, rml=False, parser=False, header=True,
				 store=False):
		# print "######################",parser,dir(parser),header,store
		# print "!!!!!!!!!!!!!!!!!",dir(self)
		super(partner_bill_summary_xls, self).__init__(name, table, rml, parser, header, store)


	def generate_xlsx_report(self, wb, data, objects):
		##Penempatan untuk template rows
		
		# xlwt.add_palette_colour("pink_header", 0x21)
		# wb.set_colour_RGB(0x21, 255, 183, 241)
		tabel_head						= wb.add_format({'bold':True,'align':'center','valign':'vcenter','fg_color':'#FFB7F1','font_color':'#000000','text_wrap':True,'num_format':'#,##0.00'})
		merge_format 					= wb.add_format({'bold': 1,'align': 'center','valign': 'vcenter'})
		numeric_format					= wb.add_format({'num_format':'#,##0.00'})
		# print "=============",dir(objects)

		objects = objects or self.parser_instance.localcontext['objects']
		_p = AttrDict(self.parser_instance.localcontext)
		ws = wb.add_worksheet("Daily Receivables")

		# ws.panes_frozen = True
		# ws.remove_splits = True
		# ws.portrait = 0  # Landscape
		# ws.fit_width_to_pages = 1
		# ws.preview_magn = 100
		# ws.normal_magn = 100
		# ws.print_scaling=100
		# ws.page_preview = False
		# ws.set_fit_width_to_pages(1)
		
		pool = objects.pool
		cr = objects._cr
		uid = objects._uid
		name = 'report.partner.bill.summ.xls'
		context = objects._context
		wizard = pool.get('res.partner.bill.print.wiz').browse(cr,uid,objects._context.get('active_id',False))
		datas = {}
		if wizard:
			datas = {'start_date':wizard.start_date,'end_date':wizard.end_date}

		# print "---------ctx2---------",dir(self.parser)

		# print "---------ctx2---------",self.uid

		now = fields.datetime.now()
		user = pool.get('res.users').browse(cr,uid,uid)
		# print "----------------------",now
		ws.merge_range('A1:J1', 'Laporan omset, pembayaran dan piutang per customer', merge_format)
		
		ws.merge_range("A3:B3","Print Date")
		ws.write("C3",now)
		ws.merge_range("A4:B4","Current System Date")
		ws.write("C4",user.name)
		
		result = _p.get_outstandings(objects=wizard,datas=datas)

		# print "==========================", result
		HEADER = ["NO","Nama Customer","Kategori","Sub Kategori","Sales","Finance","TOP(days)","Omzet","Pembayaran","Piutang"]
		col = 65
		row = 8
		for head in HEADER:
			str_len = len(head)
			ws.write(chr(col)+str(row),head,tabel_head)
			col+=1
		col=65
		row=9
		no=1
		invoice =0.0
		payment =0.0
		outstanding =0.0
		for p in result:
			d = result.get(p)
			ws.write('A'+str(row),no)
			ws.write('B'+str(row),p.name)
			ws.write('C'+str(row),p.class_ids and p.class_ids[0].name or '-')
			ws.write('D'+str(row),p.class_ids and p.class_ids[1].name or '-')
			ws.write('F'+str(row),p.user_id and p.user_id.name or '-')
			ws.write('F'+str(row),p.payment_responsible_id and p.payment_responsible_id.name or '-')
			ws.write('G'+str(row),p.property_payment_term and p.property_payment_term.name or '-')
			ws.write('H'+str(row),d.get('invoices_total',0.0),numeric_format)
			ws.write('I'+str(row),d.get('payment_total',0.0),numeric_format)
			ws.write('J'+str(row),d.get('outstandings_total',0.0),numeric_format)
			invoice+=d.get('invoices_total',0.0)
			payment+=d.get('payment_total',0.0)
			outstanding+=d.get('outstandings_total',0.0)
			no+=1
			row+=1
		# ws.write('A'+str(row),'Grand Total',tabel_head)
		ws.merge_range('A'+str(row)+':G'+str(row), 'Grand Total', tabel_head)
		ws.write('H'+str(row),invoice,tabel_head)
		ws.write('I'+str(row),payment,tabel_head)
		ws.write('J'+str(row),outstanding,tabel_head)
		
		

partner_bill_summary_xls('report.partner.bill.summ.xls', 'res.partner',
					parser=report_bill_monthly_parser)
