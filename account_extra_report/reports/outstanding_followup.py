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


class outstanding_followup_xls_parser(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(outstanding_followup_xls_parser, self).__init__(cr, uid, name,
														 context=context)
		self.context = context
		
		self.localcontext.update({
			'datetime': datetime,
			'get_outstanding': self.get_outstanding,
			
		})

	def get_outstanding(self,data,objects):
		cr = self.cr
		uid = self.uid
		qq=''
		start_date = data['start_date']
		end_date = data['end_date']
		if data['account_ids']:
			qq ="and aa in "+str(tuple(account_ids))
			qq ="and aa in "+str(tuple(account_ids))
		query="""select dummy3.name,dummy3.number1,dummy3.balance1,dummy4.number2,dummy4.balance2
			from
			(select dummy.name,count(dummy.partner_id) as number1,sum(coalesce(balance,0.00)) as balance1
			from (
			select 
			rpu.name,aml.partner_id,sum(coalesce(aml.debit,0.00)-coalesce(partial.credit,0.00)) as balance
			from account_move_line aml
			left join account_account aa on aml.account_id=aa.id
			left join res_partner rp on aml.partner_id=rp.id
			left join res_users ru on rp.payment_responsible_id=ru.id
			left join res_partner rpu on ru.partner_id=rpu.id
			left join (
				select aml2.reconcile_partial_id,sum(aml2.credit) as credit 
				from account_move_line aml2 
				where aml2.date<='%s' and aml2.reconcile_partial_id is not NULL
				group by aml2.reconcile_partial_id) partial on aml.reconcile_partial_id=partial.reconcile_partial_id
			where 
			aml.date<='%s'
			and aa.reconcile=True
			and aa.type='receivable'
			and aml.reconcile_id is NULL
			group by rpu.name,aml.partner_id
			order by rpu.name
			) dummy
			group by dummy.name
			) dummy3
			left join 
			(
			select dummy2.name,count(dummy2.partner_id) as number2,sum(coalesce(balance,0.00)) as balance2
			from (
			select 
			rpu.name,aml.partner_id,sum(coalesce(aml.debit,0.00)-coalesce(partial.credit,0.00)) as balance
			from account_move_line aml
			left join account_account aa on aml.account_id=aa.id
			left join res_partner rp on aml.partner_id=rp.id
			left join res_users ru on rp.payment_responsible_id=ru.id
			left join res_partner rpu on ru.partner_id=rpu.id
			left join (
				select aml2.reconcile_partial_id,sum(aml2.credit) as credit 
				from account_move_line aml2 
				where aml2.date<='%s'::timestamp -INTERVAL '30 days' and aml2.reconcile_partial_id is not NULL
				group by aml2.reconcile_partial_id) partial on aml.reconcile_partial_id=partial.reconcile_partial_id
			where 
			aml.date_maturity<='%s'::timestamp -INTERVAL '30 days'
			and aa.reconcile=True
			and aa.type='receivable'
			and aml.reconcile_id is NULL
			group by rpu.name,aml.partner_id
			order by rpu.name
			) dummy2
			group by dummy2.name
			) dummy4 on dummy3.name=dummy4.name
			"""%(end_date,end_date,end_date,end_date)
		
		cr.execute(query)
		result = cr.dictfetchall()
		return result

class outstanding_followup_xls(report_xls):

	def __init__(self, name, table, rml=False, parser=False, header=True,
				 store=False):
		super(outstanding_followup_xls, self).__init__(
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
		

		if data['t_report']=='outstanding_followup':
			ws = wb.add_sheet("Outstanding Followup")
			ws.panes_frozen = True
			ws.remove_splits = True
			ws.portrait = 0  # Landscape
			ws.fit_width_to_pages = 1
			ws.preview_magn = 100
			ws.normal_magn = 100
			ws.print_scaling=100
			ws.page_preview = False
			ws.set_fit_width_to_pages(1)
			
			
			ws.write_merge(0,0,0,4,"Laporan Outstanding Piutang Per Staf Collection AR",title_style_center)
			ws.write(2,0,"Current System Date",normal_bold_style_a)
			ws.write_merge(2,2,1,2,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),normal_style)
			
			ws.write(3,0,"Filtered By:",normal_bold_style_a)
			ws.write(4,0,"Start Date",normal_bold_style_a)
			ws.write(4,1,"",normal_style)
			ws.write(4,3,"End Date",normal_bold_style_a)
			ws.write(4,4,"",normal_style)
			ws.write(5,0,"Accounts",normal_bold_style_a)
			ws.write_merge(5,8,1,2,"",normal_style)
			ws.write(9,0,"Finance Name",normal_bold_style_a)
			ws.write(9,1,"Total Outstanding",normal_bold_style_a)
			ws.write(9,2,"Jumlah Customer",normal_bold_style_a)
			ws.write(9,3,"(Rp)",normal_bold_style_a)
			ws.write(9,4,"Jumlah Customer",normal_bold_style_a)
			cashflow = _p.get_outstanding(data,objects)
			row_pos=10

			SUBTOTAL_C1 =0.0
			SUBTOTAL_C2 =0.0
			SUBTOTAL_C3 =0.0
			SUBTOTAL_C4 =0.0
			GRANDTOTAL =0.0
			for cash in cashflow:
				ws.write(row_pos,0,cash['name'],normal_style)
				ws.write(row_pos,1,cash['balance1'],normal_style_float)
				ws.write(row_pos,2,cash['number1'],normal_style_float)
				ws.write(row_pos,3,cash['balance2'],normal_style_float)
				ws.write(row_pos,4,cash['number2'],normal_style_float)
				SUBTOTAL_C1 +=cash['balance1'] or 0.00
				SUBTOTAL_C2 +=cash['number1'] or 0.00
				SUBTOTAL_C3 +=cash['balance2'] or 0.00
				SUBTOTAL_C4 +=cash['number2'] or 0.00
				row_pos+=1


			ws.write(row_pos,0,"SUBTOTAL",subtotal_style2)
			ws.write(row_pos,1,SUBTOTAL_C1,subtotal_style2)
			ws.write(row_pos,2,SUBTOTAL_C2,subtotal_style2)
			ws.write(row_pos,3,SUBTOTAL_C3,subtotal_style2)
			ws.write(row_pos,4,SUBTOTAL_C4,subtotal_style2)
	
			


outstanding_followup_xls('report.outstanding.followup.report.xls', 'account.move.line',
					parser=outstanding_followup_xls_parser)
