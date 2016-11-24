from openerp.osv import fields,osv

class stock_location(osv.osv):
	_inherit = "stock.location"
	_columns = {
		"account_analytic_id":fields.many2one("account.analytic.account","Analytic Account",required=False),
	}

class stock_move(osv.osv):
	_inherit = "stock.move"
	_columns = {
		"account_analytic_id":fields.many2one("account.analytic.account","Analytic Account",required=False),
		"account_analytic_dest_id":fields.many2one("account.analytic.account","Destination Analytic Account",required=False),
		'location_id_usage': fields.selection([
						('supplier', 'Supplier Location'),
						('view', 'View'),
						('internal', 'Internal Location'),
						('customer', 'Customer Location'),
						('inventory', 'Inventory'),
						('procurement', 'Procurement'),
						('production', 'Production'),
						('transit', 'Transit Location')],
				'Location Type', required=False,
				help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
					   \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
					   \n* Internal Location: Physical locations inside your own warehouses,
					   \n* Customer Location: Virtual location representing the destination location for products sent to your customers
					   \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
					   \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
					   \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
					   \n* Transit Location: Counterpart location that should be used in inter-companies or inter-warehouses operations
					  """, select=True),
		'location_dest_id_usage': fields.selection([
						('supplier', 'Supplier Location'),
						('view', 'View'),
						('internal', 'Internal Location'),
						('customer', 'Customer Location'),
						('inventory', 'Inventory'),
						('procurement', 'Procurement'),
						('production', 'Production'),
						('transit', 'Transit Location')],
				'Location Type', required=False,
				help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
					   \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
					   \n* Internal Location: Physical locations inside your own warehouses,
					   \n* Customer Location: Virtual location representing the destination location for products sent to your customers
					   \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
					   \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
					   \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
					   \n* Transit Location: Counterpart location that should be used in inter-companies or inter-warehouses operations
					  """, select=True),
	}

	def onchange_locations(self,cr,uid,ids,location_id,location_dest_id,context=None):
		value = {'location_id_usage':False,'location_dest_id_usage':False,'account_analytic_id':False,'account_analytic_dest_id':False}
		if location_id:
			loc_id = self.pool.get('stock.location').browse(cr,uid,location_id)
			value.update({
				'location_id_usage':loc_id.usage,
				'account_analytic_id':loc_id.account_analytic_id and loc_id.account_analytic_id.id or False,
				})
		if location_dest_id:
			loc_dest_id = self.pool.get('stock.location').browse(cr,uid,location_dest_id)
			value.update({
				'location_dest_id_usage':loc_dest_id.usage,
				'account_analytic_dest_id':loc_dest_id.account_analytic_id and loc_dest_id.account_analytic_id.id or False,
				})
		return {'value':value}


class stock_quant(osv.osv):
	_inherit = "stock.quant"

	def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
		"""
		Generate the account.move.line values to post to track the stock valuation difference due to the
		processing of the given quant.
		"""
		res = super(stock_quant,self)._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
		if res and move.account_analytic_id and move.account_analytic_id.id and move.account_analytic_dest_id and move.account_analytic_dest_id.id:
			res[0][2]['analytic_account_id'] = move.account_analytic_dest_id and move.account_analytic_dest_id.id or False
			res[1][2]['analytic_account_id'] = move.account_analytic_id and move.account_analytic_id.id or False
			
		return res