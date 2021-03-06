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
from partner_balance import partner_balance
import logging
_logger = logging.getLogger(__name__)


class daily_receivable_xls_parser(partner_balance):

	def __init__(self, cr, uid, name, context):
		super(daily_receivable_xls_parser, self).__init__(cr, uid, name,
														 context=context)
		self.context = context
		
		self.localcontext.update({
			'datetime': datetime,
			'get_outstanding_fiscal':self.get_outstanding_fiscal,
			'get_outstanding_receivables':self.get_outstanding_receivables,
			'get_nonamed':self.get_nonamed,
		})

	def get_outstanding_fiscal(self,data,objects):
		fiscal = [datetime.strptime(o.date,'%Y-%m-%d').strftime('%Y') for o in objects]
		return list(set(fiscal))

	def get_outstanding_receivables2(self,data,objects):
		fiscal = [datetime.strptime(o.date,'%Y-%m-%d').strftime('%Y') for o in objects]
		fiscal = list(set(fiscal))
		res = {}
		for f in fiscal:
			res[f]={}
			for m in ['01','02','03','04','05','06','07','08','09','10','11','12']:
				res[f][m]=0.0
		for o in objects:
			dt = datetime.strptime(o.date,'%Y-%m-%d')
			year = dt.strftime('%Y')
			month = dt.strftime('%m')
			res[year][month]+=(o.debit>0.0 and o.amount_residual or 0.0) - (o.credit>0.0 and o.amount_residual or 0.0)
		return res
	
	def get_outstanding_receivables(self,data,objects):
		cr = self.cr
		start_date = data['start_date']
		end_date = data['end_date']
		account_ids = data['account_ids']

		q1=""""""
		q2=""""""
		
		if start_date:
			q1+="""aml.date>='"""+start_date+"""' and """
		if end_date:
			q1+="""aml.date<='"""+end_date+"""' and """
		if account_ids:
			q2+="""where aad.id in """+str(tuple(account_ids))+""" """
		query = """select af.name as fiscal,apd.code as period_name,af.id as fiscal_id,period_id,
					sum(coalesce(d1,0.0)-coalesce(c1,0.0)+coalesce(d2,0.0)-coalesce(c2,0.0)+coalesce(d3,0.0)-coalesce(c3,0.0)) as balance
					from 
						(select 
							aml.id,aml.account_id,aml.partner_id,aml.date,aml.period_id,aml.debit as d1,aml.credit as c1,
							aml2.id,aml2.debit as d2,aml2.credit as c2,
							aml3.id,aml3.debit as d3,aml3.credit as c3
						from account_move_line aml
							left join account_period ap on aml.period_id=ap.id
							left join account_account aa on aml.account_id=aa.id
							left join account_journal aj on aml.journal_id=aj.id
							left join res_partner rp on aml.partner_id=ap.id
							full outer join account_move_line aml2 on aml.reconcile_partial_id=aml2.reconcile_partial_id and aml2.date<='%s' and aml.id!=aml2.id
							full outer join account_move_line aml3 on aml.reconcile_id=aml3.reconcile_id and aml3.date<='%s' and aml.id!=aml3.id
						where """%(end_date,end_date)+q1+"""
						aa.type='receivable'
						and aa.reconcile=TRUE
						and aml.partner_id is not NULL
						and ((aj.type !='sale_refund' and aml.debit>0.0) or (aj.type ='sale_refund' and aml.credit>0.0))
						and (coalesce(aml.debit,0.0)-coalesce(aml.credit,0.0)+coalesce(aml2.debit,0.0)-coalesce(aml2.credit,0.0)+coalesce(aml3.debit,0.0)-coalesce(aml3.credit,0.0))>=0.0
						order by aml.partner_id, aml.id
						)dummy
					left join account_period apd on dummy.period_id=apd.id 
					left join account_account aad on dummy.account_id=aad.id 
					left join account_fiscalyear af on apd.fiscalyear_id=af.id 
					"""+q2+"""
					group by af.id,apd.id,period_id
				"""
		cr.execute(query)
		result = cr.dictfetchall()
		fiscal = []
		temp = {}
		for res in result:
			fiscal.append(res.get('fiscal',False))
		fiscal=list(set(fiscal))
		for f in fiscal:
			temp[f]={}
			for m in ['00','01','02','03','04','05','06','07','08','09','10','11','12']:
				temp[f][m]=0.00
		for o in result:
			dt = o.get('period_name',False).split('/')
			year = dt[1]
			month = dt[0]
			temp[year][month]=o.get('balance',0.00)
		return (temp,fiscal)

	def get_nonamed(self,data,objects):
		cr = self.cr
		uid = self.uid
		qq=''
		start_date = data['start_date']
		end_date = data['end_date']
		query = """select 
				sum(aml.credit-aml.debit) as balance
				from account_move_line aml
				left join account_account aa on aml.account_id=aa.id
				where aa.type='receivable'
				and aml.date <='%s'
				and partner_id is NULL"""%(end_date)
		cr.execute(query)
		result = cr.dictfetchone()
		return result or 0.00
class daily_receivable_xls(report_xls):

	def __init__(self, name, table, rml=False, parser=False, header=True,
				 store=False):
		super(daily_receivable_xls, self).__init__(
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
		

		if data['t_report']=='daily_receivable':
			ws = wb.add_sheet("Daily Receivables")
			ws.panes_frozen = True
			ws.remove_splits = True
			ws.portrait = 0  # Landscape
			ws.fit_width_to_pages = 1
			ws.preview_magn = 100
			ws.normal_magn = 100
			ws.print_scaling=100
			ws.page_preview = False
			ws.set_fit_width_to_pages(1)
			
			
			ws.write(2,0,"Current System Date",normal_bold_style_a)
			
			ws.write(3,0,"Filtered By:",normal_bold_style_a)
			ws.write(4,0,"Start Date",normal_bold_style_a)
			ws.write(4,1,"",normal_style)
			ws.write(4,3,"End Date",normal_bold_style_a)
			ws.write(4,4,"",normal_style)
			ws.write(5,0,"Accounts",normal_bold_style_a)
			
			headers = []
			TOTAL ={}

			GRANDTOTAL=0.0
			moves,fiscal = _p.result_with_partner()
			for fis in fiscal:
				headers.append(fis)
				TOTAL[fis]=0.0

			chead = (len(headers)*2)-1 >=4 and (len(headers)*2)-1 or 4
			chead2 = (len(headers)*2) >=3 and (len(headers)*2) or 3
			ws.write_merge(0,0,0,chead,"LAPORAN PIUTANG PER HARI",title_style_center)

			ws.write_merge(2,2,1,chead2,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),normal_style)
			ws.write_merge(5,7,1,chead,"",normal_style)
			col_pos = 0
			for head in sorted(headers) :
				ws.write_merge(9,9,col_pos,col_pos+1,head,th_top_style)
				col_pos+=2

			row_pos = 10
			MONTHS = {	'00':"OPENING PERIOD",'01':"JANUARI",'02':"FEBRUARI",'03':"MARET",'04':"APRIL",'05':"MEI",'06':"JUNI",
						'07':"JULI",'08':"AGUSTUS",'09':"SEPTEMBER",'10':"OCTOBER",'11':"NOVEMBER",'12':"DESEMBER"}
			
			for m in sorted(MONTHS):
				col_pos = 0
				for head in sorted(headers):
					ws.write(row_pos,col_pos,MONTHS[m],normal_style)
					ws.write(row_pos,col_pos+1,moves[head][m] or "-",normal_style_float)
					TOTAL[head]+=moves[head][m]
					GRANDTOTAL+=moves[head][m]
					col_pos+=2
				row_pos+=1
			col_pos = 0
			for head in sorted(headers):
				chr_ord =chr(ord('A') + (col_pos+1))
				ws.write(row_pos,col_pos,"TOTAL PIUTANG %s"%head,subtotal_style2)
				ws.write(row_pos,col_pos+1,xlwt.Formula("SUM($"+chr_ord+"$10:$"+chr_ord+"$"+str(row_pos)+")"),subtotal_style2)
				col_pos+=2
			row_pos+=1
			PIUTANG_NN=_p.result_without_partner()

			ws.write(row_pos,0,"Total Piutang",subtotal_style2)
			ws.write(row_pos,1,GRANDTOTAL,subtotal_style2)
			row_pos +=1
			ws.write(row_pos,0,"Tanpa Keterangan",subtotal_style2)
			ws.write(row_pos,1,PIUTANG_NN,subtotal_style2)
			row_pos +=1
			ws.write(row_pos,0,"TOTAL",subtotal_style2)
			ws.write(row_pos,1,GRANDTOTAL+	PIUTANG_NN,subtotal_style2)

daily_receivable_xls('report.daily.receivable.report.xls', 'account.move.line',
					parser=daily_receivable_xls_parser)
