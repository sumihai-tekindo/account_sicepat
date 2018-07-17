import datetime
import dateutil.parser
from openerp import models, fields, api


class purchase_order(models.Model):
	_inherit = 'purchase.order'

	date_start = fields.Date('DateStart')
	date_end = fields.Date('DateEnd')
	
class account_invoice(models.Model):
	_inherit = 'account.invoice'

	date_start = fields.Date('DateStart')
	date_end = fields.Date('DateEnd')
