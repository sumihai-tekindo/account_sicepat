# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Sicepat Ekspres Indonesia (<http://www.sicepat.com>).
#    @author: - Timotius Wigianto <https://github.com/timotiuswigianto/>
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

# 1 : imports of python lib


# 2 :  imports of openerp
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
# 3 :  imports from odoo modules
import openerp.addons.decimal_precision as dp
import base64
import datetime
from dateutil.relativedelta import relativedelta
import xlwt
import StringIO

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    @api.one
    @api.depends(
        'move_lines','move_lines.account_analytic_dest_id'
    )
    def _compute_department(self):
        analytic_dest = False
        if self.move_lines:
            for mv in self.move_lines:
                if mv.account_analytic_dest_id and mv.account_analytic_dest_id.id:
                    analytic_dest = mv.account_analytic_dest_id.id
                    break
        self.department_id = analytic_dest

    @api.one
    @api.depends(
        'stock_receipt_id', 'stock_receipt_id.state','stock_receipt_id.issue_id'
    )
    def _compute_receipt_id(self):
        self.stock_receipt_id = False
        receipt = self.env['stock.receipt'].search([('issue_id','=',self.id),('state','!=','cancel')])
        if receipt and receipt != []:
            try:
                self.stock_receipt_id = receipt[0]
            except:
                self.stock_receipt_id = receipt

    @api.one
    @api.depends(
        'date_done'
    )
    def _compute_arrival(self,):
        if self.date_done:
            date_done = self.date_done
        else:
            date_done = self.date
        dt = datetime.datetime.strptime(date_done,'%Y-%m-%d %H:%M:%S') + relativedelta(days=self.move_lines[0].account_analytic_dest_id.day_interval)
        self.date_estimate_arrival = dt.strftime('%Y-%m-%d')

    stock_receipt_id = fields.Many2one("stock.receipt","Stock Receipt",compute='_compute_receipt_id',store=True,)
    department_id = fields.Many2one("account.analytic.account","Department",compute="_compute_department", store=True, readonly=True)
    admin_id = fields.Many2one('res.users', string='Admin Cabang',
        related='department_id.user_admin_id', store=False, readonly=True,
        help="Admin Cabang")
    date_estimate_arrival = fields.Date("Estimated Arrival",compute='_compute_arrival')

    @api.cr_uid_ids_context
    def send_mail_transfer_stock(self,cr,uid,ids,context=None):
        if not context:context={}
        force_send =context.get('force_send',True)
        raise_exception = context.get('raise_exception',False)
        headstyle                = xlwt.easyxf('font: height 180, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz centre; ')
        normal_style             = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz left;',num_format_str='#,##0.00;-#,##0.00')
        normal_style_float_round = xlwt.easyxf('font: height 180, name Calibri, colour_index black; align: wrap on, vert centre, horiz right;',num_format_str='#,##0')
        for pick in self.browse(cr,uid,ids):
            workbook = xlwt.Workbook() 
            ws = workbook.add_sheet(pick.name)
            
            header = ['No.','Nama Barang','Quantity Dikirim','Satuan','Quantity Diterima','Keterangan']
            col=0

            for head in header:
                ws.write(0, col, head,headstyle)
                col+=1
            row = 1

            for line in pick.move_lines:
               ws.write(row,0,"%s"%str(row),normal_style_float_round)
               ws.write(row,1,"%s"%line.product_id.name,normal_style)
               ws.write(row,2,"%s"%line.product_uom_qty,normal_style_float_round)
               ws.write(row,3,"%s"%line.product_uom.name,normal_style)
               row+=1

            file_data=StringIO.StringIO()
            workbook.save(file_data)

            doc_vals=base64.b64encode(file_data.getvalue())
            # doc_vals=workbook
            Mail = self.pool.get('mail.mail')
            Attachment = self.pool.get('ir.attachment')
            template_id = self.pool.get('ir.model.data').get_object_reference(cr,uid,"stock_receipt","email_template_stock_transfer")
            # print "============",template_id
            values = self.pool.get('email.template').generate_email(cr,uid,template_id[1],pick.id,context=context)
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            attachment_ids = values.pop('attachment_ids', [])
            attachments = values.pop('attachments', [])
            # add a protection against void email_from
            if 'email_from' in values and not values.get('email_from'):
                values.pop('email_from')
            mail_id = Mail.create(cr,uid,values)
            mail = Mail.browse(cr,uid,mail_id)
            # manage attachments
            
            if doc_vals:
               document_vals = {
                               'name': "Pengiriman "+pick.name+".xls",
                               'datas': doc_vals,
                               'datas_fname': "Pengiriman "+pick.name+".xls",
                               'res_model': 'mail.message',
                               'res_id': mail.mail_message_id.id,
                               'type': 'binary',
                               'mimetype':"application/vnd.ms-excel",
                               }

               ir_id = Attachment.create(cr,uid,document_vals)
               attachment_ids.append(ir_id)

            if attachment_ids:
               values['attachment_ids'] = [(6, 0, attachment_ids)]
               mail.write({'attachment_ids': [(6, 0, attachment_ids)]})
            if force_send:
                Mail.send(cr, uid, [mail_id], raise_exception=raise_exception, context=context)
        return True

    @api.cr_uid_ids_context
    def do_transfer(self, cr, uid, picking_ids, context=None):
        res=super(StockPicking,self).do_transfer(cr,uid,picking_ids,context=context)
        for picking in self.browse(cr,uid,picking_ids,context=context):
            if picking.picking_type_id.default_location_src_id.usage=='internal' and picking.picking_type_id.default_location_dest_id.usage=='production':
                picking.send_mail_transfer_stock()
            else:
                continue
        return res
        

class StockReceipt(models.Model):
    # Private attributes
    _name = "stock.receipt"
    
    @api.one
    @api.depends(
        'department_id','department_id.user_admin_id'
    )
    def _compute_user(self,):
        if self.department_id:
            self.user_id = self.department_id.user_admin_id and self.department_id.user_admin_id.id or False
        else:
            self.user_id = False

    name = fields.Char("Name",states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
    department_id = fields.Many2one("account.analytic.account","Department",required=True)
    user_id = fields.Many2one('res.users', string='Admin Cabang',
        compute='_compute_user', store=True, readonly=True,
        help="Admin Cabang")
    notes = fields.Text("Notes")
    issue_id = fields.Many2one('stock.picking', 'Issue Number',
        states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]},required=True)
    partner_id = fields.Many2one('res.partner', 'Destination Address ', states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
    date= fields.Date('Inventory Date', required=True, states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
    min_date = fields.Datetime( string='Scheduled Date',states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
    origin = fields.Char("Source",states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]} )
    owner_id = fields.Many2one('res.partner', 'Owner', states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
    date_done = fields.Datetime('Date of Receipt', states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
    location_dest_id = fields.Many2one(related='stock_receipt_line.location_dest_id',states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
    state = fields.Selection([
        ('draft','Open'),
        ('receipt','Receipt'),
        ('cancel','Cancel'),
        ], string='State', readonly=True, default='draft')
    stock_receipt_line = fields.One2many('stock.receipt.line','stock_receipt_id',"Receipt Lines",states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})

    @api.model
    def create(self, vals):
        vals['user_id'] = self.env.user.id
        return super(StockReceipt, self).create(vals)

    @api.onchange('issue_id','stock_receipt_line')
    def _onchange_issue_id(self,):
        if self.issue_id:
            self.name = 'Branch Receipt of '+self.issue_id.name
            self.partner_id = self.issue_id.partner_id and self.issue_id.partner_id.id or False
            self.date = self.issue_id.date
            self.min_date = self.issue_id.min_date
            self.origin = self.issue_id.origin
            self.owner_id = self.issue_id.owner_id
            self.date_done = self.issue_id.date_done
            self.location_dest_id = self.issue_id.location_dest_id and self.issue_id.location_dest_id.id or False
            self.state = 'draft'
            self.stock_receipt_line = False
            receipt_lines = []
            linex = {}
            for line in self.issue_id.move_lines:
                linex.update({
                    'name':line.name or False,
                    'product_id':line.product_id.id or False,
                    'procure_method':line.procure_method or False,
                    'product_uom':line.product_uom.id or False,
                    'product_uos':line.product_uos and line.product_uos.id or False,
                    'product_uom_qty':line.product_uom_qty or 0.0,
                    'product_uos_qty':line.product_uos_qty or 0.0,
                    'product_receipt': 0.0,
                    'product_packaging':line.product_uom_qty or False,
                    'picking_id':line.picking_id.id or False,
                    'date':line.date or False,
                    'date_expected':line.date_expected or False,
                    'weight':line.weight or False,
                    'weight_net':line.weight_net or False,
                    # 'invoice_state':line.invoice_state or False,
                    'create_date':line.create_date or False,
                    'location_id':line.location_id and line.location_id.id or False,
                    'location_dest_id':line.location_dest_id and line.location_dest_id.id or False,
                    'account_analytic_id':line.account_analytic_id and line.account_analytic_id.id or False,
                    'account_analytic_dest_id':line.account_analytic_dest_id and line.account_analytic_dest_id.id or False,
                    })
                receipt_lines.append(linex)
                linex = {}
            self.stock_receipt_line = receipt_lines
    
    @api.multi
    def action_receipt(self):
        for receipt in self:
            if receipt.issue_id and (not receipt.issue_id.stock_receipt_id or receipt.issue_id.stock_receipt_id.id==receipt.id):
                receipt.issue_id.write({'stock_receipt_id':receipt.id})
            else:
                raise except_orm(_('Invalid Data!'),_('The Issue related to this document already linked to another receipt, you can not set this document to received.'))
        return self.write({'state':'receipt'})

    @api.multi
    def action_draft(self):
        for receipt in self:
            if receipt.issue_id and (not receipt.issue_id.stock_receipt_id or receipt.issue_id.stock_receipt_id.id==receipt.id):
                receipt.issue_id.write({'stock_receipt_id':False})
            else:
                raise except_orm(_('Invalid Data!'),_('The Issue related to this document already linked to another receipt, you can not set this document to draft.'))
        return self.write({'state':'draft'})

    @api.multi
    def action_cancel(self):
        for receipt in self:
            receipt.issue_id.write({'stock_receipt_id':False})
        return self.write({'state':'cancel'})

class StockReceiptLine(models.Model):
    _name = "stock.receipt.line"
    
    # name = fields.Char("Name")
    stock_receipt_id = fields.Many2one('stock.receipt', string='Receipt Id')
    product_id = fields.Many2one('product.product', string='Product',)
    procure_method = fields.Selection([('make_to_stock', 'Default: Take From Stock'), ('make_to_order', 'Advanced: Apply Procurement Rules')], string='Supply Method', required=True)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure',)
    product_uos = fields.Many2one('product.uom', string='Product UOS')
    product_uom_qty = fields.Float(string='Quantity Transferred', digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uos_qty = fields.Float(string='Quantity (UOS)', digits_compute=dp.get_precision('Product UoS'))
    name = fields.Char(string='Description',)
    product_packaging = fields.Many2one('product.packaging', string='Prefered Packaging')
    product_receipt = fields.Float(string="Quantity Receipt")
    picking_id= fields.Many2one('stock.picking', string='Reference')
    
    date = fields.Datetime(string='Date', )
    date_expected = fields.Datetime(string='Expected Date', )
    weight = fields.Float(string='Weight', )
    weight_net = fields.Float(string='Net Weight', )
    create_date = fields.Datetime('Creation Date', )
    
    location_id = fields.Many2one('stock.location', 'Source Location', required=True)
    account_analytic_id = fields.Many2one("account.analytic.account",string="Analytic Account",)
    location_dest_id = fields.Many2one('stock.location', string='Destination Location', )
    account_analytic_dest_id = fields.Many2one("account.analytic.account",string="Destination Analytic Account")


    @api.onchange('product_receipt','product_uom_qty')
    def _onchange_receipt_qty(self):
        if self.product_receipt and self.product_uom_qty:
            if self.product_receipt > self.product_uom_qty:
                raise ValidationError(_('Product Receipt should be less or equal than Product Transferred'))