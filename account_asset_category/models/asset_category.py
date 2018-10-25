from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime

class account_asset_asset(models.Model):
	_inherit = 'account.asset.asset'

	picking_id = fields.Many2one('stock.picking','Picking  ID')


class purchase_order_line(models.Model):
	_inherit = 'purchase.order.line'

	asset_category_id=fields.Many2one('account.asset.category','Asset Category')
	type= fields.Selection([
		('product','Product'),
		('consu','Consumable'),
		('service','Service'),
		],string='Type')
	
	@api.multi
	def onchange_product_id(self, pricelist_id, product_id, qty, uom_id,
		partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
		name=False, price_unit=False, state='draft'):
		res = super(purchase_order_line, self).onchange_product_id(pricelist_id, product_id, qty, uom_id,partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
		name=False, price_unit=False, state='draft')
		product = self.env['product.product'].search([('id','=',product_id)])
		product_type = product.product_tmpl_id.type
		value = res['value']

		value['type'] = product_type
		return res
	


class purchase_order(models.Model):
	_inherit = 'purchase.order'

	@api.model
	def _prepare_order_line_move(self, order, order_line, picking_id, group_id):
		res = super(purchase_order,self)._prepare_order_line_move(order,order_line,picking_id,group_id)
		
		for line in res :
				line.update({'asset_category_id':order_line.asset_category_id and order_line.asset_category_id.id or False})
		return res
	

class stock_move(models.Model):
	_inherit = 'stock.move'
	asset_category_id=fields.Many2one('account.asset.category','Asset Category')
		
	@api.model
	def _get_invoice_line_vals(self,  move, partner, inv_type):
		res=super(stock_move,self)._get_invoice_line_vals(move,partner,inv_type)
		
		res.update({'asset_category_id':move.asset_category_id and move.asset_category_id.id or False})

		return res

class stock_transfer_details(models.TransientModel):
	_inherit = "stock.transfer_details"

	@api.multi
	def do_detailed_transfer(self, vals):
		picking = self.picking_id
		
		asset_obj = self.env['account.asset.asset']
	
		asset_ids = []
		for line in self:
			if line.picking_id:
				picking_obj = self.env['stock.picking'].search([('id','=',line.picking_id.id)])
				# move_out_ids = self.env['stock.move'].search(cr,uid,[('quant_ids','in',quant_ids),('location_dest_id.usage','=','production'),('id','not in',existing_move_out_ids)])
				asset_ids += asset_obj.search([('name', '=', line.picking_id.name)])
		asset_obj.write({'active': False})
		
		for line in self:
			purchase_obj = self.env['purchase.order'].search([('name','=',line.picking_id.origin)])
			purchase_line = self.env['purchase.order.line'].search([('order_id','=',purchase_obj.id)])
			
			for line_obj in purchase_line:
				price = line_obj.price_unit	
				# print"000000000000000000000000000000000000000",line_obj.order_id.id
				categ= line_obj.asset_category_id.id
				if line.picking_id:
							vals = {
								'name': line.picking_id.name,
								'code': line.picking_id.origin or False,
								'picking_id': line.picking_id.id,
								'purchase_value': price,
								'partner_id': line.picking_id.partner_id.id,
								'company_id': line.picking_id.company_id.id,
								'category_id': categ,
								'purchase_date' : line.picking_id.create_date,
								'purchase_date_add' : purchase_obj.date_order,
								'account_analytic_id':line_obj.account_analytic_id.id,
								'prorata': True,
							
							}
								
							
							asset_id = asset_obj.create(vals)
							asset_obj.validate()
								
		return super(stock_transfer_details,self).do_detailed_transfer() 
