from openerp.osv import fields, osv
from openerp.tools.translate import _


class sales_order_analytic(osv.osv):
	_inherit='sale.order'
	_columns ={

		"analytic_account" : fields.many2one('account.analytic.account',string="Analytic Account")
	}


class procurement_order(osv.osv):
	_inherit = "procurement.order"

	def _run_move_create(self, cr, uid, procurement, context=None):
		res = super(procurement_order,self)._run_move_create(cr,uid,procurement,context=context)
		# res = {
  #           'name': procurement.name,
  #           'company_id': procurement.rule_id.company_id.id or procurement.rule_id.location_src_id.company_id.id or procurement.rule_id.location_id.company_id.id or procurement.company_id.id,
  #           'product_id': procurement.product_id.id,
  #           'product_uom': procurement.product_uom.id,
  #           'product_uom_qty': qty_left,
  #           'product_uos_qty': (procurement.product_uos and qty_uos_left) or qty_left,
  #           'product_uos': (procurement.product_uos and procurement.product_uos.id) or procurement.product_uom.id,
  #           'partner_id': procurement.rule_id.partner_address_id.id or (procurement.group_id and procurement.group_id.partner_id.id) or False,
  #           'location_id': procurement.rule_id.location_src_id.id,
  #           'location_dest_id': procurement.location_id.id,
  #           'move_dest_id': procurement.move_dest_id and procurement.move_dest_id.id or False,
  #           'procurement_id': procurement.id,
  #           'rule_id': procurement.rule_id.id,
  #           'procure_method': procurement.rule_id.procure_method,
  #           'origin': procurement.origin,
  #           'picking_type_id': procurement.rule_id.picking_type_id.id,
  #           'group_id': group_id,
  #           'route_ids': [(4, x.id) for x in procurement.route_ids],
  #           'warehouse_id': procurement.rule_id.propagate_warehouse_id.id or procurement.rule_id.warehouse_id.id,
  #           'date': newdate,
  #           'date_expected': newdate,
  #           'propagate': procurement.rule_id.propagate,
  #           'priority': procurement.priority,
  #       }
  		res.update({
  			'account_analytic_id': procurement.sale_line_id and procurement.sale_line_id.order_id and procurement.sale_line_id.order_id.analytic_account and procurement.sale_line_id.order_id.analytic_account.id or False,
  		})

  		return res