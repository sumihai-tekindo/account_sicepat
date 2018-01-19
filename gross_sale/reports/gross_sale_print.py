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


class gross_sale_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(gross_sale_xls_parser, self).__init__(cr, uid, name,
                                                         context=context)
        self.localcontext.update({
            'get_lines': self._get_lines,
            })
        self.context = context

    def _get_lines(self,objects):
        lines = {}
        for inv in objects:
            key = inv.partner_id.id
            for line in inv.invoice_line:
                gross_amt = inv.journal_id.type=='sale' and line.price_unit*line.quantity or 0.0
                discount_amt = inv.journal_id.type=='sale' and line.price_unit*line.quantity*line.discount/100 or 0.0
                cashback_amt = (inv.journal_id.type=='sale_refund' and inv.journal_id.cb_journal) and line.price_subtotal or 0.0
                rev_amt = (inv.journal_id.type=='sale_refund' and not inv.journal_id.cb_journal) and line.price_subtotal or 0.0
                net_amt = gross_amt - discount_amt - cashback_amt - rev_amt
                if lines.get(key):
                    lines[key]['gross_amt'] += gross_amt
                    lines[key]['discount_amt'] += discount_amt
                    lines[key]['cashback_amt'] += cashback_amt
                    lines[key]['rev_amt'] += rev_amt
                    lines[key]['net_amt'] += net_amt
                else:
                    lines[key] = {
                        'customer_name': inv.partner_id.name,
                        'gross_amt': gross_amt,
                        'discount_amt': discount_amt,
                        'cashback_amt': cashback_amt,
                        'rev_amt': rev_amt,
                        'net_amt': net_amt,
                    }
        return [v for k, v in sorted(lines.items())]

                    


class gross_sale_xls(report_xls):
    
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(gross_sale_xls, self).__init__(
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
        

        
        ws = wb.add_sheet("Gross Sale")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        ws.preview_magn = 100
        ws.normal_magn = 100
        ws.print_scaling=100
        ws.page_preview = False
        ws.set_fit_width_to_pages(1)
        
        ws.write_merge(0,0,0,4,"Gross Sale",title_style_center)
        ws.write_merge(3,3,0,1,"DATE",normal_bold_style_a)
        ws.write_merge(3,3,2,4,": "+data['form']['date_from']+" - "+data['form']['date_to'],normal_bold_style_a)
       
        headers = ["Customer", "Gross", "Discount", "Cashback","Revisi", "Net"]
                   
        col = 0
        for head in headers:
            ws.write(5,col,head,normal_bold_style_b)
            col+=1
        # print "--------------",objects
        col = 0
        row=6
        max_len = [0,0,0,0,0,0]
        for rec in sorted(_p.get_lines(objects),key=lambda x: x['customer_name']):
            ws.write(row,0,rec['customer_name'],normal_style)
            ws.write(row,1,rec['gross_amt'],normal_style)
            ws.write(row,2,rec['discount_amt'],normal_style)
            ws.write(row,3,rec['cashback_amt'],normal_style)
            ws.write(row,4,rec['rev_amt'],normal_style)
            ws.write(row,5,rec['net_amt'],normal_style)
            
            max_len[0]=len(str(rec['customer_name'])) > max_len[0] and len(str(rec['customer_name'])) or max_len[0]
            max_len[1]=len(str(rec['gross_amt'])) > max_len[1] and len(str(rec['gross_amt'])) or max_len[1]
            max_len[2]=len(str(rec['discount_amt'])) > max_len[2] and len(str(rec['discount_amt'])) or max_len[2]
            max_len[3]=len(str(rec['cashback_amt'])) > max_len[3] and len(str(rec['cashback_amt'])) or max_len[3]
            max_len[4]=len(str(rec['rev_amt'])) > max_len[4] and len(str(rec['rev_amt'])) or max_len[4]
            max_len[5]=len(str(rec['net_amt'])) > max_len[5] and len(str(rec['net_amt'])) or max_len[5]

            row+=1
            
        for x in range(0,5):
            ws.col(x).width=max_len[x]*256
        
        
        
gross_sale_xls('report.gross.sale.xls', 'account.invoice', parser=gross_sale_xls_parser)
            
        