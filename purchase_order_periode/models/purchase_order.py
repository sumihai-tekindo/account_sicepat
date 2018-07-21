import datetime
import dateutil.parser
from openerp import models, fields, api


class purchase_order(models.Model):
	_inherit = 'purchase.order'

	date_start = fields.Date('Periode Awal Sewa')
	date_end = fields.Date('Periode Akhir Sewa')
	
	
class account_invoice(models.Model):
	_inherit = 'account.invoice'

	date_start = fields.Date('Periode Awal Sewa')
	date_end = fields.Date('Periode Akhir Sewa')