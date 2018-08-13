from openerp import models, fields, api
import time 
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import datetime as dt

class asset_rent(models.Model):
	_name = "asset.rent"

	start_date = fields.Date("Start Date",required=True)
	end_date = fields.Date("End Date",required=True)
	date_invoice =  fields.Date("Invoice Date",required=True)
	rent = fields.Boolean(string='Rent')
	branch = fields.Many2one('account.analytic.account','Branch')
	#address = fiel
	department_id = fields.Many2one('account.invoice.department','Department')
	supplier_id = fields.Many2one('res.partner','Supplier')
	product_id = fields.Many2one('product.product','Category Invoice Line')
	building_type = fields.Many2one('account.analytic.account','Building Type')
	biaya_sewa = fields.Float('Rental Costs')
	deposit = fields.Float('Deposit')
	total = fields.Float('Total')
	state= fields.Selection([('open', 'In Progress'), ('toclose','To Close'), ('closed', 'Terminated')])
