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


class stock_move_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(stock_move_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.context = context


class stock_move_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(stock_move_xls, self).__init__(
            name, table, rml, parser, header, store)


    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ##Penempatan untuk template rows
        title_style                     = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        title_style_center                = xlwt.easyxf('font: height 220, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center; ')
        normal_style                     = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz left;',num_format_str='#,##0.00;-#,##0.00')
        normal_style_center                = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center;')
        normal_style_float                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
        normal_style_float_round         = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0')
        normal_style_float_bold         = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz right;',num_format_str='#,##0.00;-#,##0.00')
        normal_bold_style                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        normal_bold_style_a             = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left; ')
        normal_bold_style_b             = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on;pattern: pattern solid, fore_color gray25; align: wrap on, vert centre, horiz left; ')
        th_top_style                     = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick')
        th_both_style_left                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz left;')
        th_both_style                     = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom thick')
        th_bottom_style                 = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:bottom thick')
        th_both_style_dashed             = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz center; border:top thick, bottom dashed',num_format_str='#,##0.00;-#,##0.00')
        th_both_style_dashed_bottom     = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right; border:bottom dashed',num_format_str='#,##0.00;-#,##0.00')
        
        subtotal_title_style            = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left; borders: top thin, bottom thin;')
        subtotal_style                      = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: bottom thin;',num_format_str='#,##0;-#,##0')
        subtotal_style2                     = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; borders: top thin, bottom thin;',num_format_str='#,##0.00;-#,##0.00')
        total_title_style                   = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;')
        total_style                         = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.0000;(#,##0.0000)')
        total_style2                    = xlwt.easyxf('font: name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right;pattern: pattern solid, fore_color gray25; borders: top thin, bottom thin;',num_format_str='#,##0.00;(#,##0.00)')
        subtittle_top_and_bottom_style  = xlwt.easyxf('font: height 240, name Times New Roman, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        

        
        ws = wb.add_sheet("Stock Move")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling=100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,4,"Stock Move",title_style_center)
        ws.write_merge(3,3,0,1,"PERIODE",normal_bold_style_a)
        ws.write_merge(3,3,2,4,": "+data['start_date']+" - "+data['end_date'],normal_bold_style_a)
       
        headers = ["Source Location", "Destination Location", "Account Analytic", "Date", "Product", "Description", "Refrence","Picking Type", "Quantity","Unit Of Measure", "Price Unit", "State"]
                   
        col = 0
        for head in headers:
            ws.write(5,col,head,normal_bold_style_b)
            col+=1
            
        col = 0
        row=6
        max_len = [0,0,0,0,0,0,0,0,0,0,0,0]
        for rec in objects:
            print "-------------------------",rec.product_id.name_get()
            prod = rec.product_id and rec.product_id.name_get() and rec.product_id.name_get()[0][1] or rec.product_id.name or ''
            ws.write(row,0,rec.location_id.complete_name,normal_style)
            ws.write(row,1,rec.location_dest_id.complete_name,normal_style)
            ws.write(row,2,rec.account_analytic_dest_id.name,normal_style)
            ws.write(row,3,rec.date_expected,normal_style)
            ws.write(row,4,rec.name,normal_style)
            ws.write(row,5,prod,normal_style)
            ws.write(row,6,rec.picking_id.name,normal_style)
            ws.write(row,7,rec.picking_type_id.name,normal_style)
            ws.write(row,8,rec.product_uom_qty,normal_style)
            ws.write(row,9,rec.product_uom.name,normal_style)
            ws.write(row,10,rec.price_unit,normal_style)
            ws.write(row,11,rec.state,normal_style)
            
            max_len[0]=len(str(rec.location_id.complete_name)) > max_len[0] and len(str(rec.location_id.complete_name)) or max_len[0]
            max_len[1]=len(str(rec.location_dest_id.complete_name)) > max_len[1] and len(str(rec.location_dest_id.complete_name)) or max_len[1]
            max_len[2]=len(str(rec.account_analytic_dest_id.name)) > max_len[2] and len(str(rec.account_analytic_dest_id.name)) or max_len[2]
            max_len[3]=len(str(rec.date_expected)) > max_len[3] and len(str(rec.date_expected)) or max_len[3]
            max_len[4]=len(str(rec.name)) > max_len[4] and len(str(rec.name)) or max_len[4]
            max_len[5]=len(str(prod)) > max_len[5] and len(str(prod)) or max_len[5]
            max_len[6]=len(str(rec.picking_id.name)) > max_len[6] and len(str(rec.picking_id.name)) or max_len[6]
            max_len[7]=len(str(rec.picking_type_id.name)) > max_len[7] and len(str(rec.picking_type_id.name)) or max_len[7]
            max_len[8]=len(str(rec.product_uom_qty)) > max_len[8] and len(str(rec.product_uom_qty)) or max_len[8]
            max_len[9]=len(str(rec.product_uom.name)) > max_len[9] and len(str(rec.product_uom.name)) or max_len[9]
            max_len[10]=len(str(rec.price_unit)) > max_len[10] and len(str(rec.price_unit)) or max_len[10]
            max_len[11]=len(str(rec.state)) > max_len[11] and len(str(rec.state)) or max_len[11]

            row+=1
            
        for x in range(0,12):
            ws.col(x).width=max_len[x]*256
        
        
        
stock_move_xls('report.stock.move.xls', 'stock.move', parser=stock_move_xls_parser)
            
        