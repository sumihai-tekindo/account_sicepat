from datetime import datetime
from openerp.osv import fields,osv
from openerp.tools.translate import _


class purchase_requisition_line(osv.osv):
	_inherit = "purchase.requisition.line"


	def stock_out(self, cr, uid, ids,stock_out):
		if self.stock_out:
			return {
			'view_type': 'form',
			'flags': {'action_buttons': True},
			'view_mode': 'kanban,form',
			'res_model': 'stock.picking.type',
			'target': 'current',
			'res_id': 'stock.picking',
			'type': 'ir.actions.act_window'
			
		} 
	# def onchange_product_id(self, cr, uid, ids, product_id, product_uom_id, parent_analytic_account, analytic_account, parent_date, date, context=None):
	# 	oc_res = super(purchase_requisition_line,self).onchange_product_id(cr, uid, ids, product_id, product_uom_id, parent_analytic_account, analytic_account, parent_date, date, context=context)
	# 	if(product_id):
	# 		product = self.pool.get('product.product').browse(cr,uid,product_id,context=context)
	# 		if (product.default_code=='Asset'):
	# 			warning={
	# 				'title':'WARNING',
	# 				'message':"There are %s %s for %s in stock"%(product.qty_available,product.uom_id.name,product.name)
	# 				}
	# 			oc_res.update({'warning':warning})	
	# 	return oc_res	
	