from openerp import models, fields, api
import time 
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import datetime as dt
###LAMA
class purchasereq(models.Model):
	_inherit = 'purchase.requisition'
	

	@api.model
	def _default_reff(self):
		return self._context.get('product_type','biaya')

	ordering_date = fields.Date(default=fields.Date.today)
	date_end = fields.Datetime('Bid Submission Deadline', required=True, default=fields.Datetime.now)


	schedule_date = fields.Date(string="Schedule Date",required=True,default=lambda *x: (date.today()+ relativedelta(days=+3)).strftime('%Y-%m-%d'))
	product_type = fields.Selection([('biaya','Biaya'),('asset','Asset'),('material','Material')],'Product Type', default=_default_reff)
	multiple_rfq_per_supplier = fields.Boolean(default=True)

##responsible
# class purchasereq1(models.Model):
# 	_name = 'purchase.requisition.user.id'
	
# 	name1 = fields.Char('user_id')
###employee
class purchasereq2(models.Model):
	_inherit = "res.users"

	employee = fields.Many2one('res.users','employee',required=True)
	@api.onchange('employee')  # if these fields are changed, call  method
	def check_change(self):
		if self.employee:
			self.user_id = self.employee.name

