import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class res_partner_bill_print_wiz(models.Model):
	_name = "res.partner.bill.print.wiz"

	start_date= fields.Date("Start Date",required=True)
	end_date= fields.Date("End Date",required=True)
	rep_type = fields.Selection([('pdf','PDF'),('xls','XLS')],'Report Type',default='pdf',required=True)
	partner_ids = fields.Many2many('res.partner','bill_wiz_partner_rel','partner_id','wiz_id',string='Selected Partners')
	
	@api.model
	def default_get(self, fields):
		res = super(res_partner_bill_print_wiz, self).default_get(fields)
		
		partner = self.env['res.partner'].search([('id','=',self._context.get('active_id',False))])
		current_date = datetime.datetime.today()
		partner_date = current_date
		if partner.billing_date:
			partner_date = datetime.datetime.strptime(partner.billing_date,'%Y-%m-%d')
		end_date = partner_date.strftime('%Y-%m-'+partner_date.strftime('%d'))

		start_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
		if partner.billing_period=='weekly':
			start_date-=relativedelta(days=7)
		elif partner.billing_period=='monthly':
			start_date-=relativedelta(months=1)
		partner_ids = self._context.get('active_ids',False)
		start_date = start_date.strftime('%Y-%m-%d')
		res.update({'end_date':end_date,'start_date':start_date,'partner_ids':partner_ids})
		return res


	@api.multi
	def create_report_bill(self):
		self.ensure_one()
		datas = {'start_date':self.start_date,'end_date':self.end_date,'ids':self._context.get('active_ids')}
		print "----------------",datas
		if self.rep_type=='pdf':
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'customer_bill_mail.bill_monthly_report_per_customer',
				'datas': datas,
				# 'ids': self._context.get('active_ids',False)
				}
		else:
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'partner.bill.summ.xls',
				'datas': datas,
				# 'ids': self
				}


	