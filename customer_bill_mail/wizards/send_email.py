import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.osv import osv
from openerp import tools

class res_partner_bill_mail_wiz(models.Model):
	_name = "res.partner.bill.mail.wiz"



	start_date= fields.Date("Start Date",required=False)
	end_date= fields.Date("End Date",required=False)
	# rep_type = fields.Selection([('pdf','PDF'),('xls','XLS')],'Report Type',default='pdf',required=False)
	partner_ids = fields.Many2many('res.partner','mail_bill_wiz_partner_rel','partner_id','wiz_id',string='Selected Partners')

	@api.model
	def default_get(self, fields):
		res = super(res_partner_bill_mail_wiz, self).default_get(fields)
		
		# partner = self.env['res.partner'].search([('id','=',self._context.get('active_id',False))])
		# current_date = datetime.datetime.today()
		# partner_date = current_date
		# if partner.billing_date:
		# 	partner_date = datetime.datetime.strptime(partner.billing_date,'%Y-%m-%d')
		# end_date = partner_date.strftime('%Y-%m-'+partner_date.strftime('%d'))

		# start_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
		# if partner.billing_period=='weekly':
		# 	start_date-=relativedelta(days=7)
		# elif partner.billing_period=='monthly':
		# 	start_date-=relativedelta(months=1)
		partner_ids = self._context.get('active_ids',False)
		# start_date = start_date.strftime('%Y-%m-%d')
		# res.update({'end_date':end_date,'start_date':start_date,'partner_ids':partner_ids})
		res.update({'partner_ids':partner_ids})
		return res

	@api.multi
	def get_outstandings(self,objects=None,datas=None):
		# print "--sdfsfsd------------",dir(objects)
		# cr=self.cr
		# uid=self.uid
		ids=self.ids
		context={}
		# ids =[94401]
		# print "=====enter zone=======",self.objects
		# for ob in dir(self.objects):
		#     print "=====enter zone=======",ob,"===",eval("self.objects."+ob),""
		
		# print "objects===========",objects
		if not objects:
			try:
				objects =self.objects
			except:
				objects = self
		# print "xxxxxxxxxxxxxxxxxx",objects
		if objects and objects._name=='res.partner.bill.mail.wiz':
			ids = objects.partner_ids and [x.id for x in objects.partner_ids]
			partners = objects.partner_ids
		else:
			partners = objects


		# print "-----------",partners
		if not context:context={}
		result = {}
		journal_bank = self.env['account.journal'].search([('type','in',('cash','bank'))])
		journal_invoice = self.env['account.journal'].search([('type','not in',('bank', 'cash', 'purchase', 'purchase_refund'))])
		account_ids = self.env['account.account'].search([('type','=','receivable')])

		today =datetime.datetime.today()
		std =False
		try:
			std = objects.start_date
		except:
			std = False

		if not std and datas:
			try:
				std = datas.get('start_date')
			except:
				std=std
		start_date = {}
		end_date = {}
		if not std:
			for partner_id in partners:
				# print "@@@@@@@@@@@@@@@@@@@@",partner_id
				if not partner_id.billing_period:
					start_date.update({partner_id:datetime.date.today().strftime('%Y-%m-%d')})
					end_date.update({partner_id:datetime.date.today().strftime('%Y-%m-%d')})
				else:
					if partner_id.billing_period=='weekly':
						billing_nth_day = partner_id.billing_nth_day

						# 0 = Monday, 1 = Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
						curr_week_day = today.weekday()

						# print "=----------------=>",curr_week_day,"-",billing_nth_day-1

						if billing_nth_day-1 > curr_week_day:
							end_date.update({partner_id:today-relativedelta(days=(7-billing_nth_day-1+curr_week_day))})
							start_date.update({partner_id:end_date.get(partner_id,0)-relativedelta(days=7)})
							# print "-------1---------",end_date
						elif billing_nth_day-1==curr_week_day:
							end_date.update({partner_id:today})
							start_date.update({partner_id:today-relativedelta(days=7)})
							# print "-------2---------",end_date
						else:
							norm = billing_nth_day-1
							if norm<0:
								norm =abs(norm)
							end_date.update({partner_id:today-relativedelta(days=curr_week_day-norm)})
							start_date.update({partner_id:end_date.get(partner_id,0)-relativedelta(days=7)})
							# print "-------3---------",end_date
					elif partner_id.billing_period=='monthly':
						monthly_date=datetime.datetime.strptime(partner_id.billing_date,'%Y-%m-%d').strftime('%d')
						try:
							new_date = "%s-%s-%s"%(today.strftime('%Y'),today.strftime('%m'),monthly_date)
						except:
							try:
								new_date = "%s-%s-%s"%(today.strftime('%Y'),today.strftime('%m'),'30')
							except:
								try:
									new_date = "%s-%s-%s"%(today.strftime('%Y'),today.strftime('%m'),'28')
								except:
									new_date = "%s-%s-%s"%(today.strftime('%Y'),today.strftime('%m'),'29')

						new_end_date = datetime.datetime.strptime(new_date,'%Y-%m-%d')
						if new_end_date>=today:
							end_date.update({partner_id:today})
						else:
							end_date.update({partner_id:new_end_date})
						start_date.update({partner_id:end_date.get(partner_id,0) - relativedelta(months=1)})

					# print "----------------",start_date.get(partner_id).strftime('%Y-%m-%d')

					end_date.update({partner_id:end_date.get(partner_id).strftime('%Y-%m-%d')})
					start_date.update({partner_id:start_date.get(partner_id).strftime('%Y-%m-%d')})
		elif std and objects and not datas:
			for partner_id in partners:
				# print "==============",self.objects
				start_date.update({partner_id:objects.start_date})
				end_date.update({partner_id:objects.end_date})
		elif std and objects and datas:
			# print "==============",datas,type(datas),datas.get('start_date')
			for partner_id in partners:
				start_date.update({partner_id:datas.get('start_date',False)})
				end_date.update({partner_id:datas.get('end_date',False)})

		# print "==========",start_date,"xxxxx",end_date
		for partner_id in partners:
			first_date=False
			last_date=False
			total_inv=0.0
			total_paid=0.0
			total_outstanding=0.0
			
			domain_inv = [
						('partner_id', '=', partner_id.id), 
						('move_id.state', '=', 'posted'), 
						('account_id', 'in', [x.id for x in account_ids]), 
						('journal_id', 'in', [y.id for y in journal_invoice]), 
						('debit', '>', 0), 
						('date','>=',start_date.get(partner_id,False)),
						('date','<=',end_date.get(partner_id,False)),
					]
			domain_payment = [('partner_id','=',partner_id.id),
					('account_id', 'in', [x.id for x in account_ids]) ,('credit','>',0.0),('journal_id','in',[z.id for z in journal_bank]),('date','>=',start_date.get(partner_id,False)),
						('date','<=',end_date.get(partner_id,False))]
			domain_outstandings = [
						('partner_id', '=', partner_id.id), 
						('move_id.state', '=', 'posted'), 
						('account_id', 'in', [x.id for x in account_ids]), 
						('journal_id', 'in', [y.id for y in journal_invoice]), 
						('debit', '>', 0), 
						('date','<=',end_date.get(partner_id,False)),
					]
			
			mv_inv = self.env['account.move.line'].search(domain_inv,order="date asc")
			# mv_inv = self.pool.get('account.move.line').browse(cr,uid,mv_inv_ids,context=context)

			mv_payment = self.env['account.move.line'].search(domain_payment,order="date asc")
			

			mv_outstanding = self.env['account.move.line'].search(domain_outstandings,order="date asc")
			# mv_outstanding = self.pool.get('account.move.line').browse(cr,uid,mv_outstanding_ids,context=context)

			date_dict = {}
			payment_dict = {}
			outstanding_dict ={}
			for inv in mv_inv:
				key = inv.date
				if date_dict.get(key,False):
					date_dict[key]['total']=date_dict.get(key).get('total') + inv.debit
					
				else:
					date_dict[key]={
						'date':inv.date,
						'total':inv.debit,
						'currency_id':inv.company_id.currency_id.id,
						'due_date':inv.date_maturity,
						}
				total_inv+= inv.debit
				# if not first_date:
				#     first_date=key
				# last_date=key

			for pay in mv_payment:
				key = pay.date
				if payment_dict.get(key,False):
						payment_dict[key]['total']=payment_dict.get(key).get('total') + pay.credit-pay.amount_residual
				else:
					payment_dict[key]={
						'date':pay.date,
						'total':pay.credit-pay.amount_residual,
						'currency_id':pay.company_id.currency_id.id,
						'payment_date':pay.date,
						}
				total_paid+=pay.credit-pay.amount_residual

			for out in mv_outstanding:
				key = out.date
				if outstanding_dict.get(key,False):
					outstanding_dict[key]['total']+=out.amount_residual
					
				else:
					outstanding_dict[key]={
						'date':out.date,
						'total':out.amount_residual,
						'currency_id':out.company_id.currency_id.id,
						'due_date':out.date_maturity,
						}
				total_outstanding+=out.amount_residual
				if not first_date:
					first_date=key
				last_date=key
			

		
			result.update({
				partner_id.id:{
					# 'partner':partner_id,
					'start_date':start_date.get(partner_id,False),
					'end_date':end_date.get(partner_id,False),
					'start_date_outstanding':first_date,
					'invoices': date_dict,
					'invoices_total':total_inv,
					'payment': payment_dict,
					'payment_total':total_paid,
					'outstandings' : outstanding_dict,
					'outstandings_total': total_outstanding,
					'currency_id': partner_id.company_id.currency_id.id
					}
				})
		# print "--------------",result
		return result


	@api.multi
	def create_bill_mail(self,):
		self.ensure_one()
		# import base64
		if self.partner_ids and len(self.partner_ids)==1:
			if not self.partner_ids[0].opt_out:
				if not self.partner_ids[0].email:
					raise except_orm(_('No Email Defined!'),_("You must define email address for this customer!"))
				else:
					if self.partner_ids[0].billing_period=='monthly':
						template = self.env.ref('customer_bill_mail.email_template_bill_invoice_monthly', False)
					else:
						template = self.env.ref('customer_bill_mail.email_template_bill_invoice_weekly', False)
					# template = self.pool.get('ir.model.data').get_object_reference(cr,uid,"customer_bill_mail","email_template_bill_payment")
					compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
					# compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
					outstandings = self.get_outstandings(objects=self.partner_ids[0],datas={'start_date':self.start_date,'end_date':self.end_date})
					print "======{'94401': ======",outstandings
					ctx = dict(
						default_model='res.partner',
						active_model='res.partner',
						default_use_template=bool(template),
						default_template_id=template and template.id or False,
						composition_mode='comment',
						# default_composition_mode='comment',
						default_partner_to=self.partner_ids[0].id,
						start_date = self.start_date,
						end_date = self.end_date,
						res_ob=outstandings,
						res_id = self.partner_ids[0].id,
						active_id=self.partner_ids[0].id,
						default_res_id=self.partner_ids[0].id,
						active_ids = [x.id for x in self.partner_ids],
						# active_domain=[('id','in',[x.id for x in self.partner_ids])]
					)
					# print "xxxxxxxxxxxxxxxxxxxxxx",ctx
					return {
						'name': _('Compose Email for Billing'),
						'type': 'ir.actions.act_window',
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'mail.compose.message',
						'src_model': 'res.partner',
						# 'res_id':(x.id for x in self.partner_ids),
						'default_partner_to': '${object.id or \'\'}',
						'views': [(compose_form.id, 'form')],
						'view_id': compose_form.id,
						'target': 'new',
						'context': ctx,
					}
		else:
			Mail = self.env['mail.mail']
			Attachment=self.env['ir.attachment']
			import base64
			for p in self.partner_ids:
				# att_ids =False
				if not p.opt_out:
					if not p.email:
						raise except_orm(_('No Email Defined!'),_("You must define email address for customer named %s (id:%s)!"%(p.name,p.id)))
					else:
						outstandings = self.get_outstandings(objects=self.partner_ids[0],datas={'start_date':self.start_date,'end_date':self.end_date})
						# print "=====responsible============>",p.payment_responsible_id.partner_id.email
						compose_ctx = dict(
							start_date = self.start_date,
							end_date = self.end_date,
							res_ob=outstandings,
							# default_composition_mode="mass_mail",
							# active_model = 'res.partner',
						# 	active_id=False,
							# active_ids=[p.id],
						# 	override_reply_to = "%s <%s>"%(p.payment_responsible_id.name, p.payment_responsible_id.partner_id.email),
								   )
						if p.billing_period=='monthly':
							# template = self.env.ref('customer_bill_mail.email_template_bill_invoice_monthly', False).id
							template = self.env['ir.model.data'].get_object_reference("customer_bill_mail","email_template_bill_invoice_monthly")
						else:
							# template = self.env.ref('customer_bill_mail.email_template_bill_invoice_weekly', False).id
							template = self.env['ir.model.data'].get_object_reference("customer_bill_mail","email_template_bill_invoice_weekly")


						values = self.pool['email.template'].generate_email(self._cr,self._uid,template[1],p.id,context=compose_ctx)
						# for k in values.keys():
						# 	if k !='attachments':
						# 		print k,"==",values.get(k)
						# # print "-----------",type(values)
						values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
						attachment_ids = values.pop('attachment_ids', [])
						attachments = values.pop('attachments', [])
						# values['body_html'] = values['body_html']
						# values['body'] = values['body_html']
						values['reply_to'] = "%s <%s>"%(p.payment_responsible_id.name, p.payment_responsible_id.partner_id.email)
						values['email_cc'] = "%s <%s>"%(p.payment_responsible_id.name, p.payment_responsible_id.partner_id.email)

						tmpl = self.env['email.template'].browse(template[1])
						report_xml_pool = self.env['ir.actions.report.xml']

						
						report_name = self.pool['email.template'].render_template(self._cr, self._uid, tmpl.report_name, tmpl.model, p.id, context=compose_ctx)
						if tmpl.report_template:
							report = report_xml_pool.browse(tmpl.report_template.id)
							report_service = report.report_name
							tofile, format = self.pool['report'].get_pdf(self._cr, self._uid, [p.id],report_service, context=compose_ctx), 'pdf'

						mail_id = Mail.create(values)
						
						
						if tofile:					
							document_vals = {
									   'name': report.report_name+"."+format,
									   'datas': base64.b64encode(tofile),
									   'datas_fname': report.report_name+"."+format,
									   'res_model': 'mail.message',
									   'res_id': mail_id.mail_message_id.id,
									   'type': 'binary',
									   'mimetype':"application/pdf",
									   }

							ir_id = Attachment.create(document_vals)
							attachment_ids.append(ir_id.id)

						# values['attachment_ids'] = [(6, 0, attachment_ids)]
						mail_id.write({'attachment_ids': [(6, 0, attachment_ids)]})
		return True


# class email_template(osv.osv):
# 	inherit ="email.template"

# 	@api.v8
# 	def send_mail(self, template_id, res_id, force_send=False, raise_exception=False):
# 		return email_template.send_mail(
# 			self._model, self._cr, self._uid, self, res_id, force_send=force_send,raise_exception=raise_exception)

