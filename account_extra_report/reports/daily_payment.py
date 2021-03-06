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


class daily_payment_xls_parser(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(daily_payment_xls_parser, self).__init__(cr, uid, name,
														 context=context)
		self.context = context
		
		self.localcontext.update({
			'datetime': datetime,
			'get_cust_payment': self.get_cust_payment,
			
		})

	def get_cust_payment(self,data,objects):
		cr = self.cr
		uid = self.uid
		qq=''
		start_date = data['start_date']
		end_date = data['end_date']
		if data['account_ids']:
			qq ="and name in "+str(tuple(account_ids))
		query="""select 
			coalesce(daily.id,periodic.id,aadc.id) as id,
			coalesce(daily.name,periodic.name,aadc.name) as name,
			coalesce(daily.debit,0.0) as daily_debit, 
			coalesce(periodic.debit,0.0) as periodic_debit

			from (select 
			aa.id,aa.name,sum(aml.debit) as debit
			from account_move_line aml
			left join account_account aa on aml.account_id = aa.id
			left join account_account_type aat on aa.user_type=aat.id
			left join account_move_line aml2 on aml.move_id=aml.id 
			left join account_account aat2 on aml2.account_id=aat2.id and aat2.type='receivable'
			where 
			aat.code='bank'
			and aa.type='liquidity'
			and aml.date='%s'
			and aml.debit>0.0
			group by aa.id,aa.name
			) daily
			full outer join 
			(select 
			aa.id,aa.name,sum(aml.debit) as debit
			from account_move_line aml
			left join account_account aa on aml.account_id = aa.id
			left join account_account_type aat on aa.user_type=aat.id
			left join account_move_line aml2 on aml.move_id=aml.id 
			left join account_account aat2 on aml2.account_id=aat2.id and aat2.type='receivable'
			where 
			aat.code='bank'
			and aa.type='liquidity'
			and aml.date>='%s'
			and aml.date<='%s'
			and aml.debit>0.0
			group by aa.id,aa.name) periodic on periodic.id=daily.id
			full outer join 
			(select aa3.id,aa3.name 
			from account_account aa3 
			left join account_account_type aat3 on aa3.user_type=aat3.id 
			where aa3.type='liquidity' and aat3.code='bank'
			) aadc on aadc.id=periodic.id
			"""%(end_date,start_date,end_date)+qq+"""
			order by name
			"""
		
		cr.execute(query)
		result = cr.dictfetchall()
		return result

class daily_payment_xls(report_xls):

	def __init__(self, name, table, rml=False, parser=False, header=True,
				 store=False):
		super(daily_payment_xls, self).__init__(
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
		

		if data['t_report']=='daily_payment':
			ws = wb.add_sheet("Daily Customer Payments")
			ws.panes_frozen = True
			ws.remove_splits = True
			ws.portrait = 0  # Landscape
			ws.fit_width_to_pages = 1
			ws.preview_magn = 100
			ws.normal_magn = 100
			ws.print_scaling=100
			ws.page_preview = False
			ws.set_fit_width_to_pages(1)
			
			
			ws.write_merge(0,0,0,2,"Laporan Penerimaan Uang dari Pelunasan Piutang",title_style_center)
			ws.write(2,0,"Current System Date",normal_bold_style_a)
			ws.write_merge(2,2,1,2,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),normal_style)
			
			ws.write(3,0,"Filtered By:",normal_bold_style_a)
			ws.write(4,0,"Start Date",normal_bold_style_a)
			ws.write(4,1,"",normal_style)
			ws.write(4,3,"End Date",normal_bold_style_a)
			ws.write(4,4,"",normal_style)
			ws.write(5,0,"Accounts",normal_bold_style_a)
			ws.write_merge(5,8,1,2,"",normal_style)
			ws.write(9,0,"TRANSFER MASUK DARI CUST.")
			ws.write(9,1,"%s"%(data['end_date']),normal_bold_style_a)
			ws.write(9,2,"%s s/d %s"%(data['start_date'],data['end_date']),normal_bold_style_a)
			data_bank = _p.get_cust_payment(data,objects)
			row_pos=10
			SUBTOTAL =0.0
			GRANDTOTAL =0.0
			for bank in data_bank:
				ws.write(row_pos,0,bank['name'],normal_style)
				ws.write(row_pos,1,bank['daily_debit'],normal_style_float)
				ws.write(row_pos,2,bank['periodic_debit'],normal_style_float)
				SUBTOTAL +=bank['daily_debit']
				GRANDTOTAL +=bank['periodic_debit']
				row_pos+=1
			ws.write(row_pos,0,"Total Uang Masuk",subtotal_style2)
			ws.write(row_pos,1,SUBTOTAL,subtotal_style2)
			ws.write(row_pos,2,GRANDTOTAL,subtotal_style2)
			


daily_payment_xls('report.daily.payment.report.xls', 'account.move.line',
					parser=daily_payment_xls_parser)
