import datetime
import dateutil.parser
from openerp import fields, models, api
from openerp.tools.translate import _

class account_invoice(models.Model):
	_inherit = "account.invoice"

	@api.one
	@api.depends('move_id.line_id.reconcile_id.line_id',
		'move_id.line_id.reconcile_partial_id.line_partial_ids')
	
	def _compute_payments(self):
		
		res = super(account_invoice,self)._compute_payments()
		if self.payment_ids:
			self.payment_date = self.payment_ids[0].date
		return res
	
	payment_date = fields.Date('Payment Date',compute='_compute_payments', store=True)