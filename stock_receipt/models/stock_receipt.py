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

# 3 :  imports from odoo modules
import openerp.addons.decimal_precision as dp

class StockReceipt(models.Model):
    # Private attributes
    _name = "stock.receipt"
    
    name = fields.Char("Name")
    issue_id = fields.Many2one('stock.picking', 'Issue Number',
        states={'receipt': [('readonly', True)],'cancel': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', 'Destination Address ', )
    date= fields.Date('Inventory Date', required=True, )
    min_date = fields.Datetime( string='Scheduled Date')
    origin = fields.Char("Source", )
    owner_id = fields.Many2one('res.partner', 'Owner', )
    date_done = fields.Datetime('Date of Receipt', )
    location_dest_id = fields.Many2one(related='stock_receipt_line.location_dest_id')
    state = fields.Selection([
        ('draft','Open'),
        ('receipt','Receipt'),
        ('cancel','Cancel'),
        ], string='State', readonly=True, default='draft')
    stock_receipt_line = fields.One2many('stock.receipt.line','stock_receipt_id')
    
class StockReceiptLine(models.Model):
    _name = "stock.receipt.line"
    
    name = fields.Char("Name")
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
    weight_net = fields.Float(string='Weight', )
    invoice_state = fields.Many2one('stock.location', string='Destination Location', )
    create_date = fields.Datetime('Creation Date', )
    
    location_id = fields.Many2one('stock.location', 'Source Location', required=True)
    account_analytic_id = fields.Many2one("account.analytic.account",string="Analytic Account",)
    location_dest_id = fields.Many2one('stock.location', string='Destination Location', )
    account_analytic_dest_id = fields.Many2one("account.analytic.account",string="Destination Analytic Account")