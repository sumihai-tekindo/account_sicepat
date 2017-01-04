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
from xlwt import Formula as fm
from datetime import datetime
from openerp.osv import orm
from openerp.addons.report_xls.report_xls import report_xls
# from openerp.addons.report_xls.utils import rowcol_to_cell, _render

import time
from openerp.report import report_sxw
from openerp.tools.translate import translate
import logging

# from .nov_account_journal import nov_journal_print
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class daily_cashflow_xls_parser(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(daily_cashflow_xls_parser, self).__init__(cr, uid, name,
														 context=context)
		self.context = context
		
		self.localcontext.update({
			'datetime': datetime,
			'get_cashflow': self.get_cashflow,
			
		})

	def get_cashflow(self,data,objects):
		cr = self.cr
		uid = self.uid
		qq=''
		start_date = data['start_date']
		end_date = data['end_date']
		if data['account_ids']:
			qq ="and name in "+str(tuple(account_ids))
		query="""select coalesce(receivable.date,payment.date) as date,coalesce(receivable.credit,0.00) as credit,coalesce(payment.debit,0.00) as debit,payment.id,payment.name
			from (select
			aml.date,sum(coalesce(aml.credit,0.00)) as credit
			from account_move_line aml
			left join account_account aa on aml.account_id=aa.id
			left join account_journal aj on aml.journal_id=aj.id
			where 
			aml.date='%s'
			and aa.type='receivable'
			and aa.reconcile=True
			and aj.type!='sale_refund'
			and aml.credit>0.0
			and (aml.reconcile_id is NOT NULL or aml.reconcile_partial_id is NOT NULL)
			group by aml.date
			) receivable
			full outer join (
			select aml2.date,sum(coalesce(aml2.debit,0.00)) as debit,aid.id,aid.name
			from account_move_line aml2
			left join account_move_line aml3 on aml2.reconcile_id=aml3.reconcile_id or aml2.reconcile_partial_id=aml3.reconcile_partial_id
			left join account_account aa2 on aml2.account_id=aa2.id
			left join account_journal aj2 on aml2.journal_id=aj2.id
			left join account_invoice ai on aml3.move_id=ai.move_id
			left join account_invoice_department aid on ai.department_id=aid.id
			where 
			aml2.date='%s'
			and aa2.type='payable'
			and aa2.reconcile=True
			and aj2.type!='purchase_refund'
			and aml2.debit>0.0
			and (aml2.reconcile_id is NOT NULL or aml2.reconcile_partial_id is NOT NULL)
			group by aml2.date,aid.id,aid.name 
			) payment
			on receivable.date=payment.date
			"""%(start_date,start_date)
		
		cr.execute(query)
		result = cr.dictfetchall()
		return result

class daily_cashflow_xls(report_xls):

	def __init__(self, name, table, rml=False, parser=False, header=True,
				 store=False):
		super(daily_cashflow_xls, self).__init__(
			name, table, rml, parser, header, store)


	def generate_xls_report(self, _p, _xs, data, objects, wb):
		##Penempatan untuk template rows
		title_style 					= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
		title_style_center				= xlwt.easyxf('font: height 220, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center; ')
		normal_style 					= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz left;',num_format_str='#,##0.00;-#,##0.00')
		normal_style_center				= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center;')
		normal_style_float 				= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
		normal_style_float_round 		= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0')
		normal_style_float_bold 		= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
		normal_bold_style 				= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
		normal_bold_style_a 			= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
		normal_bold_style_b 			= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on;pattern: pattern solid, fore_color gray25; align: wrap on, vert centre, horiz left; ')
		th_top_style 					= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick')
		th_both_style_left 				= xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left;')
		th_both_style 					= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom thick')
		th_bottom_style 				= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:bottom thick')
		th_both_style_dashed 			= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom dashed',num_format_str='#,##0.00;-#,##0.00')
		th_both_style_dashed_bottom 	= xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right; border:bottom dashed',num_format_str='#,##0.00;-#,##0.00')
		
		subtotal_title_style			= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left; borders: top thin, bottom thin;')
		subtotal_style				  	= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: bottom thin;',num_format_str='#,##0;-#,##0')
		subtotal_style2				 	= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: top thin, bottom thin;',num_format_str='#,##0.00;-#,##0.00')
		total_title_style			   	= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;')
		total_style					 	= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.0000;(#,##0.0000)')
		total_style2					= xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.00;(#,##0.00)')
		subtittle_top_and_bottom_style  = xlwt.easyxf('font: height 240, name Times New Roman, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
		

		if data['t_report']=='daily_cashflow':
			ws = wb.add_sheet("Daily Cashflow")
			ws.panes_frozen = True
			ws.remove_splits = True
			ws.portrait = 0  # Landscape
			ws.fit_width_to_pages = 1
			ws.preview_magn = 100
			ws.normal_magn = 100
			ws.print_scaling=100
			ws.page_preview = False
			ws.set_fit_width_to_pages(1)
			
			
			ws.write_merge(0,0,0,4,"Laporan Cashflow per Hari",title_style_center)
			ws.write(2,0,"Current System Date",normal_bold_style_a)
			ws.write_merge(2,2,1,2,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),normal_style)
			
			ws.write(3,0,"Filtered By:",normal_bold_style_a)
			ws.write(4,0,"Start Date",normal_bold_style_a)
			ws.write(4,1,"",normal_style)
			ws.write(4,3,"End Date",normal_bold_style_a)
			ws.write(4,4,"",normal_style)
			ws.write(5,0,"Accounts",normal_bold_style_a)
			ws.write_merge(5,8,1,2,"",normal_style)
			ws.write(9,0,"Keterangan Penerimaan")
			ws.write(9,1,"Pelunasan AR",normal_bold_style_a)
			ws.write(9,2,"Keterangan Pengeluaran",normal_bold_style_a)
			ws.write(9,3,"Pengeluaran",normal_bold_style_a)
			ws.write(9,4,"Surplus/Defisit",normal_bold_style_a)
			cashflow = _p.get_cashflow(data,objects)
			row_pos=10
			SUBTOTAL_D =0.0
			SUBTOTAL_C =0.0
			GRANDTOTAL =0.0
			prev_date = False
			for cash in cashflow:
				
				ws.write(row_pos,0,cash['date'],normal_style)
				if cash['date']!=prev_date:
					ws.write(row_pos,1,cash['credit'],normal_style_float)
					prev_date = cash['credit']
					SUBTOTAL_C +=cash['credit'] or 0.00
				ws.write(row_pos,2,cash['name'],normal_style_float)
				ws.write(row_pos,3,cash['debit'],normal_style_float)
				SUBTOTAL_D +=cash['debit'] or 0.00
				row_pos+=1

			GRANDTOTAL =SUBTOTAL_C-SUBTOTAL_D
			ws.write(row_pos,0,"SUBTOTAL",subtotal_style2)
			ws.write(row_pos,1,SUBTOTAL_C,subtotal_style2)
			ws.write(row_pos,3,SUBTOTAL_D,subtotal_style2)
			ws.write(row_pos,4,GRANDTOTAL,subtotal_style2)
			


daily_cashflow_xls('report.daily.cashflow.report.xls', 'account.move.line',
					parser=daily_cashflow_xls_parser)
