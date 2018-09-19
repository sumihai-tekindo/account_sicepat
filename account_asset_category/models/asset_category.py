from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime

class purchase_order_line(models.Model):
	_inherit = 'purchase.order.line'

	asset_category_id=fields.Many2one('account.asset.category','Asset Category')

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

