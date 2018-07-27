from openerp import models, fields, api
import time 
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import datetime as dt


class purchasereq(models.Model):
	_inherit = 'purchase.requisition'
	
	@api.model
	def _default_reff(self):
		return self._context.get('product_type','biaya')

	@api.onchange('koordinator_wilayah')
	def koordinator_wilayah(self):
		if self.koordinator_wilayah:
			self.id = self.account_analytic_account.koordinator_wilayah.id


	ordering_date = fields.Date(default=fields.Date.today)
	date_end = fields.Datetime('Bid Submission Deadline', required=True, default=fields.Datetime.now)
	employee=fields.Many2one('res.users','Requested By',required=False)

	schedule_date = fields.Date(string="Schedule Date",required=True,default=lambda *x: (date.today()+ relativedelta(days=+3)).strftime('%Y-%m-%d'))
	product_type = fields.Selection([('biaya','Biaya'),('asset','Asset'),('material','Material')],'Product Type', default=_default_reff)
	multiple_rfq_per_supplier = fields.Boolean(default=True)

	koordinator_wilayah = fields.Many2one('hr.employee','employee',required=False)

	@api.onchange('employee')  # if these fields are changed, call  method
	def check_change(self):
		if self.employee:
			self.user_id = self.employee.name

		
	# @api.multi# if these fields are changed, call  method
	# def stock_out(self):
	# 	if self.stock_out:
	# 		return {
	# 		'view_type': 'form',
	# 		'view_mode': 'tree,form,calendar',
	# 		'res_model': 'stock.picking',
	# 		'target': 'new act_window',
	# 		'res_id': 'stock.vpicktree',
	# 		'type': 'ir.actions.act_window'
	# 	} 