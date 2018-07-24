from openerp import api
from openerp.osv import osv, fields

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
		department_id=order.department_id and order.department_id.id or False
		res.update({'department_id':department_id})
		return  res