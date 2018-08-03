from openerp import models, fields, api
import time 
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import datetime as dt
from openerp.exceptions import Warning

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
	department = fields.Many2one('account.invoice.department','Department')
	
	schedule_date = fields.Date(string="Schedule Date",required=True,default=lambda *x: (date.today()+ relativedelta(days=+3)).strftime('%Y-%m-%d'))
	product_type = fields.Selection([('biaya','Biaya'),('asset','Asset'),('material','Material')],'Product Type', default=_default_reff)
	multiple_rfq_per_supplier = fields.Boolean(default=True)

	koordinator_wilayah = fields.Many2one('hr.employee','employee',required=False)

	@api.onchange('employee')
		
	def check_change(self):
		if self.employee:
			self.user_id = self.employee.name

# class purchase_requisition_line(models.Model):
# 	_inherit = 'purchase.requisition_line'

	@api.onchange('product_id')
	def onchange_product_id(self):	
		schedule_hari = self.env['Product_template.'].search([('schedule_hari','=',self.id.id)])
		duration = self.env['res_company.'].search([('duration','=',self.id.id)])
		#cek schedule hari ke product template
		if(self.Product_template.schedule_hari.id==0):
			#if exists, ambil value dari product template
			self.schedule_date.id = self.res_company.duration
			
		else:
			#if not exists, ambil dari res company.duration
			self.schedule_date.id = self.Product_template.schedule_hari.id
			#res=super(requisition_line,self).onchange_product_id(self, cr, uid, ids, product_id, product_uom_id, parent_analytic_account, analytic_account, parent_date, date, context=None):
