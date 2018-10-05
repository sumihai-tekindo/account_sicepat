from openerp import models, fields, api, _


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    # cancel_reason_id = fields.Many2one('purchase.order.cancel.reason',string="Reason for cancellation", readonly=True,default=1)
    cancel_reason = fields.Char('Reason Cancel')
	

class purchase_order_cancel_reason(models.Model):
    _name = 'purchase.order.cancel.reason'
    _description = 'Purchase Order Cancel Reason'

    name = fields.Char('Reason', required=True, translate=True)
