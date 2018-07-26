from openerp import api
from openerp.osv import osv, fields

class purchase_line_invoice(osv.osv_memory):
	_inherit = 'purchase.order.line_invoice'

	def _make_invoice_by_partner(self, cr, uid, partner, orders, lines_ids, context=None):
		"""
			create a new invoice for one supplier
			@param cr : Cursor
			@param uid : Id of current user
			@param partner : The object partner
			@param orders : The set of orders to add in the invoice
			@param lines : The list of line's id
		"""
		purchase_obj = self.pool.get('purchase.order')
		account_jrnl_obj = self.pool.get('account.journal')
		invoice_obj = self.pool.get('account.invoice')
		name = orders and orders[0].name or ''
		journal_id = account_jrnl_obj\
			.search(cr, uid, [('type', '=', 'purchase')], context=None)
		journal_id = journal_id and journal_id[0] or False
		a = partner.property_account_payable.id
		inv = {
			'name': name,
			'origin': name,
			'type': 'in_invoice',
			'journal_id': journal_id,
			'reference': partner.ref,
			'account_id': a,
			'partner_id': partner.id,
			'department_id': orders[0].department_id and orders[0].department_id.id or False,
			'invoice_line': [(6, 0, lines_ids)],
			'currency_id': orders[0].currency_id.id,
			'comment': " \n".join([order.notes for order in orders if order.notes]),
			'payment_term': orders[0].payment_term_id.id,
			'fiscal_position': partner.property_account_position.id
		}
		inv_id = invoice_obj.create(cr, uid, inv, context=context)
		purchase_obj.write(cr, uid, [order.id for order in orders], {'invoice_ids': [(4, inv_id)]}, context=context)
		return inv_id


class purchase_order(osv.osv):
	_inherit ="purchase.order"

	_columns = {
		'department_id': fields.many2one('account.invoice.department', 'Department', readonly=True, states={'draft': [('readonly', False)]}, copy=False, ondelete='set null'),
	}

	def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
		"""Prepare the dict of values to create the new invoice for a
		   purchase order. This method may be overridden to implement custom
		   invoice generation (making sure to call super() to establish
		   a clean extension chain).

		   :param browse_record order: purchase.order record to invoice
		   :param list(int) line_ids: list of invoice line IDs that must be
									  attached to the invoice
		   :return: dict of value to create() the invoice
		"""
		res = super(purchase_order,self)._prepare_invoice( cr, uid, order, line_ids, context=context)
		department_id = order.department_id and order.department_id.id or False
		res.update({'department_id': department_id})
		return res
	
	def action_picking_create(self, cr, uid, ids, context=None):
		for order in self.browse(cr, uid, ids):
			picking_vals = {
				'picking_type_id': order.picking_type_id.id,
				'partner_id': order.partner_id.id,
				'date': order.date_order,
				'origin': order.name,
				'department_inv_id': order.department_id and order.department_id.id or False
			}
			picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals, context=context)
			self._create_stock_moves(cr, uid, order, order.order_line, picking_id, context=context)
		return picking_id
