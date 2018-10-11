import time
from lxml import etree

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp

class account_voucher(models.Model):
	_inherit ="account.voucher"

	
	mail_sent= fields.Boolean("Mail Sent", default=False)
	

	# _defaults={
	# 	'mail_sent':False
	# }

	@api.multi
	def action_payment_sent(self):
		""" Open a window to compose an email, with the edi invoice template
			message loaded by default
		"""
		# if not context:context={}
		# print "-------------called-1--------------",context
		# if context.get('type','payment')!='receipt':
		# 	return False
		self.ensure_one()
		data = self
		print "-------------called1--------------",data.type
		if data.partner_id.opt_out:
			return True
		elif not data.partner_id.opt_out and not data.partner_id.email:
			raise except_orm(_('No Email Defined!'),
                _("You must define email address for this customer!"))
		else:
			template = self.env.ref('customer_bill_mail.email_template_bill_payment', False)
			# template = self.pool.get('ir.model.data').get_object_reference(cr,uid,"customer_bill_mail","email_template_bill_payment")
			compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
			# compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
			ctx = dict(
				default_model='account.voucher',
				default_res_id=self.id,
				default_use_template=bool(template),
				default_template_id=template and template.id or False,
				default_composition_mode='comment',
				default_partner_to=self.partner_id.id,
				#mark_invoice_as_sent=True,
			)
			return {
				'name': _('Compose Email for Payment Notification'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'mail.compose.message',
				'views': [(compose_form.id, 'form')],
				'view_id': compose_form.id,
				'target': 'new',
				'context': ctx,
			}
