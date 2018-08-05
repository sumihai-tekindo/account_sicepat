from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime


class account_invoice_line(models.Model):
	_inherit = "account.invoice.line"

	def get_received_qty(self,move_lines):
		picking_items={}
		for x in move_lines:
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
				#qty_uom_trf = self.env['product.uom']._compute_qty_obj(x.product_uom, x.product_qty, x.purchase_line_id.product_uom, round=True, rounding_method='UP', context=None)

			picking_items.update({
				x.product_id.id:qty_po - qty_already_received
				})
		return picking_items

	@api.multi
	def write(self,vals):
		self.ensure_one()
		invoice = self.invoice_id
		

		invoice_items = {}
		res=False
		qty_receipt = 0.0
		qty_po = 0.0
		qty_invoice= 0.0
		if self.move_line_ids:

			receipts = self.get_received_qty(self.move_line_ids)
			qty_invoice = vals.get('quantity',self.quantity)
			qty_receipt = receipts.get(self.product_id.id,0.0)
			qty_po 	= self.move_line_ids[0].purchase_line_id.product_qty
			#qty_po = self.move_line_ids and self.move_line_ids[0].purchase_line_id and self.move_line_ids[0].purchase_line_id.product_qty
	
			
		if (qty_receipt>0 and qty_invoice > qty_po) or ((not qty_receipt or qty_receipt==0.0) and qty_invoice>qty_po) :
			raise Warning(_('You cannot receive product more than Receipt / PO quantity \'%s\'.') % self.product_id.name)
		else	:
			res=super(account_invoice_line,self).write(vals)
		return res

		