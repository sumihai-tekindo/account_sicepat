import datetime
import dateutil.parser
from openerp import fields, models, api
from datetime import datetime
from openerp.tools.translate import _


class purchase_order(models.Model):
	_inherit = "purchase.order"

	date_start = fields.Date('Start Rent')
	date_end = fields.Date('End Rent')
	sewa = fields.Boolean(string='Rent', default=False)
	#department= fields.Many2one('account.invoice.department','Department')


	@api.onchange('sewa')
	def _compute_hide(self):
		if self.sewa ==True:
			date_start = True
			date_end = True
		else:
			date_start = False
			date_end = False



class account_invoice(models.Model):
	_inherit = "account.invoice"

	date_start = fields.Date('Start Rent')
	date_end = fields.Date('End Rent')
	sewa = fields.Boolean(string='Rent', default=False)

	@api.onchange('sewa')
	def _compute_hide(self):
		if self.sewa ==True:
			date_start = True
			date_end = True
		else:
			date_start = False
			date_end = False