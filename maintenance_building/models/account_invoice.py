from openerp import models, fields, api, _

class account_invoice(models.Model):
	_inherit = 'account.invoice'


	aset_rental_id = fields.Many2one("asset.rental","Asset Rental")