import datetime
from lxml import etree
import math
import pytz
import urlparse

import openerp
from openerp import tools, api
from openerp.osv import osv, fields
from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _
from openerp.addons.base.res.res_partner import format_address
from openerp.report import report_sxw


class res_partner(osv.Model):
	_description = 'Partner'
	_inherit = "res.partner"

	_columns = {
		'billing_period'	: fields.selection([('daily','Daily'),('weekly','Weekly'),('monthly','Monthly'),('custom','Custom')],"Billing Period"),
		'billing_date'		: fields.date('Billing Date'),
		'billing_nth_day'	: fields.integer("Day of period",help="Monday:1, Tuesday:2, Wednesday:3, Thursday:4, Friday:5, Saturday:6, Sunday:7"),
		'billing_python_scrip': fields.text("Python Script to compute billing date"),
		'mail_payment_template_id': fields.many2one('email.template','Custom Payment Template'),
		'mail_invoicing_template_id': fields.many2one('email.template','Custom Invoicing Template'),
		'mail_overdue_template_id': fields.many2one('email.template','Custom Overdue Template'),	
		'whatsapp_number'	: fields.char('Whatsapp Number'),
		'line_account'		: fields.char('Line Account'),		
	}

	_defaults = {
		
	}


	def sent_billing_schedule(self,cr,uid,context=None):
		if not context:
			context={}
		return True

		# partner = self.pool.get('res.partner').search(cr,uid)

	def formatLang(self, value, digits=None, date=False, date_time=False, grouping=True, monetary=False, dp=False, currency_obj=False):
		# print "-----------------",dir(self)
		cr = self._cr
		uid = self._uid
		context={}
		rml_parser = report_sxw.rml_parse(cr, uid, 'reconciliation_widget_aml', context=context)
		return rml_parser.formatLang(value, digits=None, date=False, date_time=False, grouping=True, monetary=False, dp=False, currency_obj=False)