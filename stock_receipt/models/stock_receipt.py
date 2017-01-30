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
from openerp.exceptions import except_orm, Warning, RedirectWarning
# 3 :  imports from odoo modules
import openerp.addons.decimal_precision as dp

class StockPicking(models.Model):
    _inherit = "stock.picking"


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


    stock_receipt_id = fields.Many2one("stock.receipt","Stock Receipt",compute='_compute_receipt_id',store=True,)

class StockReceipt(models.Model):
    # Private attributes
    _name = "stock.receipt"
    
    name = fields.Char("Name",states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
    issue_id = fields.Many2one('stock.picking', 'Issue Number',
        states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
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
    product_uom_qty = fields.Float(string='Quantity', digits_compute=dp.get_precision('Product Unit of Measure'))
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