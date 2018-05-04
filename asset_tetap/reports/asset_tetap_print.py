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


class asset_tetap_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(asset_tetap_xls_parser, self).__init__(cr, uid, name,context=context)
        self.context = context

        
class asset_tetap_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(asset_tetap_xls, self).__init__(
            name, table, rml, parser, header, store)


    def generate_xls_report(self, _p, _xs, data, objects, wb):

        grouping = {}
        for group in objects:
            if group.category_id in grouping.keys():
                dummy = grouping.get(group.category_id,[])
                dummy.append(group)
                grouping.update({group.category_id:dummy})
            else:
                grouping.update({group.category_id:[group]})

        ##Penempatan untuk template rows
        title_style = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        title_style_center = xlwt.easyxf('font: height 220, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center; ')
        normal_style = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz left;',num_format_str='#,##0.00;-#,##0.00')
        normal_style_center = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center;')
        normal_style_float = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
        normal_style_float_round = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0')
        normal_style_float_bold = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
        normal_bold_style = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        normal_bold_style_a = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        normal_bold_style_b = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on;pattern: pattern solid, fore_color gray25; align: wrap on, vert centre, horiz left; ')
        th_top_style = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick')
        th_both_style_left = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left;')
        th_both_style = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom thick')
        th_bottom_style = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:bottom thick')
        th_both_style_dashed = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom dashed',num_format_str='#,##0.00;-#,##0.00')
        th_both_style_dashed_bottom = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right; border:bottom dashed',num_format_str='#,##0.00;-#,##0.00')
        
        subtotal_title_style = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left; borders: top thin, bottom thin;')
        subtotal_style = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: bottom thin;',num_format_str='#,##0;-#,##0')
        subtotal_style2 = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: top thin, bottom thin;',num_format_str='#,##0.00;-#,##0.00')
        total_title_style = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;')
        total_style = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.0000;(#,##0.0000)')
        total_style2 = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.00;(#,##0.00)')
        subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Times New Roman, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        

        
        for group in grouping.keys():
            ws = wb.add_sheet(group.name)
            ws.panes_frozen = True
            ws.remove_splits = True
            ws.portrait = 0  # Landscape
            ws.fit_width_to_pages = 1
            ws.preview_magn = 100
            ws.normal_magn = 100
            ws.print_scaling=100
            ws.page_preview = False
            ws.set_fit_width_to_pages(1)
            
            ws.write_merge(0,0,0,6,"ASSET TETAP",title_style_center)
            ws.write_merge(3,3,0,2,"PERIODE",normal_bold_style_a)
            ws.write_merge(3,3,3,6,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
           
            max_len = [0,0,0,0,0,0,0,0,0]
            headers = ["No.","NAMA","TANGGAL PEMBELIAN","PENYUSUTAN","HARGA PEROLEHAN","AKUMULASI PENYUSUTAN","NILAI BUKU","INVOICE","WH TRANSFER"]
            col = 0
            for head in headers:
                max_len[col]=len(head)
                ws.write(5,col,head,normal_bold_style_b)
                col+=1

            row=6
            no=1
            for rec in grouping.get(group,[]): 
                ws.write(row,0,no,normal_style_float_round)
                ws.write(row,1,rec.name,normal_style)
                ws.write(row,2,rec.purchase_date,normal_style)
                ws.write(row,3,rec.method_number,normal_style_float_round)
                ws.write(row,4,rec.purchase_value,normal_style_float)

                depreciated_value = 0.0
                depr=rec.depreciation_line_ids and rec.depreciation_line_ids[0]
                if depr:
                    end_date = datetime.strptime(data['end_date'],'%Y-%m-%d')
                    for line in rec.depreciation_line_ids:
                        dep_date = datetime.strptime(line.depreciation_date,'%Y-%m-%d')
                        if dep_date<=end_date and line.move_check == True:
                            depreciated_value += line.amount
#                         else:
#                             break
                ws.write(row,5,depreciated_value,normal_style_float)
                netbook_value = rec.purchase_value - depreciated_value
                ws.write(row,6,netbook_value,normal_style_float)
                if rec.invoice_id:
                    ws.write(row,7,rec.invoice_id.number,normal_style)
                    ws.write(row,8,rec.invoice_id.origin or '',normal_style)

                max_len[0]=len(str(no))+3 > max_len[0] and len(str(no))+3 or max_len[0]
                max_len[1]=len(str(rec.name))+3 > max_len[1] and len(str(rec.name))+3 or max_len[1]
                max_len[2]=len(str(rec.purchase_date))+3 > max_len[2] and len(str(rec.purchase_date))+3 or max_len[2]
                max_len[3]=len(str(rec.method_number))+3 > max_len[3] and len(str(rec.method_number))+3 or max_len[3]
                max_len[4]=len(str(rec.purchase_value))+3 > max_len[4] and len(str(rec.purchase_value))+3 or max_len[4]
                max_len[5]=len(str(depreciated_value))+3 > max_len[5] and len(str(depreciated_value))+3 or max_len[5]
                max_len[6]=len(str(netbook_value))+3 > max_len[6] and len(str(netbook_value))+3 or max_len[6]
                if rec.invoice_id:
                    max_len[7]=len(str(rec.invoice_id.number))+3 > max_len[7] and len(str(rec.invoice_id.number))+3 or max_len[7]
                    max_len[8]=len(str(rec.invoice_id.origin or ''))+3 > max_len[8] and len(str(rec.invoice_id.origin or ''))+3 or max_len[8]

                no+=1
                row+=1
            
            for x in range(9):
                ws.col(x).width=max_len[x]*256 > 65535 and 65535 or max_len[x]*256



asset_tetap_xls('report.report.asset.tetap.xls', 'account.asset.asset', parser=asset_tetap_xls_parser)