from openerp import models, fields, api, _


class purchase_order_cancel(models.TransientModel):

	_name = 'purchase.order.cancel'
	# _description = __doc__

	reason_id = fields.Many2one('purchase.order.cancel.reason',string='Reason',required=True,default=1)
	cancel_reason = fields.Char('Reason Cancel')

	@api.multi
	def action_cancel(self):
		self.ensure_one()
		act_close = {'type': 'ir.actions.act_window_close'}
		purchase_ids = self._context.get('active_ids')
		print "purchase_ids",purchase_ids
		if purchase_ids is None:
			return act_close
		assert len(purchase_ids) == 1, "Only 1 purchase ID expected"
		purchase = self.env['purchase.order'].browse(purchase_ids)
		purchase.cancel_reason_id = self.reason_id.id
		purchase.cancel_reason = self.cancel_reason
		purchase.action_cancel()
		return act_close
