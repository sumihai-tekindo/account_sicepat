from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime


class stock_transfer_details(models.TransientModel):
	_inherit = "stock.transfer_details"

	@api.one
	def do_detailed_transfer(self):
		###### start stock checking qty with PO #####
		
		picking = self.picking_id
		picking_items = {}
		res=False
		for x in picking.move_lines:
			qty_already_received = 0.0
			received_qty = 0.0
			returned_qty = 0.0
			qty_po = x.purchase_line_id.product_qty
			for y in x.purchase_line_id.move_ids:
				if y.state=='done' and y.id!=x.id:
					received_qty += self.env['product.uom']._compute_qty_obj(y.product_uom, y.product_uom_qty, x.purchase_line_id.product_uom, round=True, rounding_method='UP', context=None)
					if y.returned_move_ids :
						for z in y.returned_move_ids:
							if z.state=='done':
								returned_qty+= self.env['product.uom']._compute_qty_obj(z.product_uom, z.product_uom_qty, x.purchase_line_id.product_uom, round=True, rounding_method='UP', context=None)

				qty_already_received = received_qty - returned_qty
			qty_uom_trf = self.env['product.uom']._compute_qty_obj(x.product_uom, x.product_qty, x.purchase_line_id.product_uom, round=True, rounding_method='UP', context=None)

			picking_items.update({
				x.product_id.id:qty_po - qty_already_received
				})
			
			
		
		for item in self.item_ids:
			if item.product_id and item.product_id.id and item.product_id.id in picking_items.keys():
				if item.quantity>picking_items.get(item.product_id.id,0.0):
					raise Warning(_('You cannot receive product more than PO quantity \'%s\'.') % item.product_id.name)
				else:
					res=super(stock_transfer_details,self).do_detailed_transfer()
			else:
				raise Warning(_('You cannot receive product that doesn\'t belong in PO \'%s\'.') % item.product_id.name)
		###### end stock checking qty with PO #####
		
		return res 