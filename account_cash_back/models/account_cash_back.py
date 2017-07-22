from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta


class account_cashback_rule(osv.osv):
	_name = "account.cashback.rule"
	_columns = {
		"name"				: fields.char("Rule Name",required=True),
		"rules"				: fields.text("Rules Condition",required=True),
		"next_disc"			: fields.float("Discount Percentage",required=True),
		"cash_back_amt_rule": fields.text("Cashback Amount Rule",required=True),
		"product_id"		: fields.many2one("product.product","Cash Back Product",required=True),
		"partner_ids"		: fields.many2many('res.partner','cashback_rule_partner_rel', 'rule_id', 'partner_id', 'Applied Customers',),
		"journal_id"		: fields.many2one("account.journal","Journal",required=True),
		"department_id"		: fields.many2one("account.invoice.department","Department",required=False),
		"active"			: fields.boolean("Active"),
		"date_start"		: fields.date("Effective Start Date",required=True),
		"date_end"			: fields.date("Effective End Date",required=True),
		"sequence"			: fields.integer("Computation Sequence",required=True),
		"account_analytic_id": fields.many2one("account.analytic.account","Analytic Account"),
	}
	_defaults = {
		"rules":"# Use this fields : current_disc, omzet_before_disc, omzet_after_disc, omzet_paid, deposit, cash_back_amt, proposed_disc",
		"cash_back_amt_rule":"# Use this fields : current_disc, omzet_before_disc, omzet_after_disc, omzet_paid, deposit, cash_back_amt, proposed_disc",
		"date_start"		: lambda *a: '2017-01-01',	
		"date_end"			: lambda *a: '2017-01-31',	
		"sequence"			: lambda *a: 1,	
		"active"			: True
	}
	_order = "date_start desc, sequence asc"

class account_cashback(osv.osv):
	_name = "account.cashback"
	_columns = {
		"name"			: fields.char("Name",required=True),
		"start_date"	: fields.date("Start Date",required=True),
		"end_date"		: fields.date("End Date",required=True),
		"line_ids"		: fields.one2many("account.cashback.line","cashback_id","Cashback Lines"),
		"state"			: fields.selection([('draft','Draft'),('inprogress','In Progress'),('done','Done'),('cancelled','Cancelled')],"Status",required=True),
	}

	_defaults = {
	"state":'draft',
	}
	def compute_cashback(self,cr,uid,ids,context=None):
		if not context: context={}
		for cb in self.browse(cr,uid,ids):
			for cb_line in cb.line_ids:
				context.update({'start_date':cb_line.start_date,'end_date':cb_line.end_date})
			self.pool.get('account.cashback.line').compute_cashback_lines(cr,uid,[cx.id for cx in cb.line_ids],context=context)
		return True

	def submit_cashback(self,cr,uid,ids,context=None):
		if not context:context={}
		for cb in self.browse(cr,uid,ids,context=context):
			cb.write({'state':'submitted'})
		return True

	def approve_cashback(self,cr,uid,ids,context=None):
		if not context:context={}
		for cb in self.browse(cr,uid,ids,context=context):
			cb.write({'state':'approved'})
		return True

	def cancel_cashback(self,cr,uid,ids,context=None):
		if not context:context={}
		for cb in self.browse(cr,uid,ids,context=context):
			cb.write({'state':'cancelled'})
		return True
	
	def set_to_draft(self,cr,uid,ids,context=None):
		if not context:context={}
		for cb in self.browse(cr,uid,ids,context=context):
			cb.write({'state':'draft'})
		return True
	def create_invoices(self,cr,uid,ids,context=None):
		if not context:context={}
		for cb in self.browse(cr,uid,ids,context=context):
			self.pool.get('account.cashback.line').create_invoice(cr,uid,[x.id for x in cb.line_ids],context=context)
		return True
	def update_partner_disc(self,cr,uid,ids,context=None):
		if not context:context={}
		for cb in self.browse(cr,uid,ids,context=context):
			self.pool.get('account.cashback.line').update_partner_disc(cr,uid,[x.id for x in cb.line_ids],context=context)
		return True

	def delete_zero_omzet(self,cr,uid,ids,context=None):
		if not context:context={}
		for cb in self.browse(cr,uid,ids,context=context):
			partner = []
			for cb_line in cb.line_ids:
				context.update({'start_date':cb_line.start_date,'end_date':cb_line.end_date})
				partner.append(cb_line.name.id)
			self.pool.get('account.cashback.line').delete_zero_omzet(cr,uid,[x.id for x in cb.line_ids],partner,context=context)
		return True

	def delete_zero_cashback(self,cr,uid,ids,context=None):
		if not context:context={}
		for cb in self.browse(cr,uid,ids,context=context):
			lines = []
			for cb_line in cb.line_ids:
				if cb_line.cash_back_amt<=0.0:
					lines.append(cb_line.id)
			self.pool.get('account.cashback.line').unlink(cr,uid,lines)
		return True


	# def generate_customer_refund(self,cr,uid,ids,context=None):
	# 	for cb in self.browse(cr,uid,ids,context=context):
	# 		invoice_ids=[]
	# 		if cb.state=='approved':
	# 			return False
	# 		a = cb.name.property_account_payable.id
	# 		name =cb.cashback_id and cb.cashback_id.name or cb.name.name
	# 		expense_account = cb.product_id.property_account_expense and cb.product_id.property_account_expense.id or \
	# 						cb.product_id.categ_id and cb.product_id.categ_id.property_account_expense_categ and cb.product_id.categ_id.property_account_expense_categ.id or False

	# 		inv = {
	# 			'name': name,
	# 			'origin': name,
	# 			'type': 'out_refund',
	# 			'journal_id': journal_id,
	# 			'reference': cb.name.ref,
	# 			'account_id': a,
	# 			'partner_id': cb.name.id,
	# 			'currency_id': user.company_id.currency_id.id,
	# 			'comment': name,
	# 			'payment_term': cb.name.property_supplier_payment_term and cb.name.property_supplier_payment_term.id or False,
	# 			'fiscal_position': cb.name.property_account_position.id,
	# 			'department_id': cb.department_id and cb.department_id.id,
	# 			'user_id': uid,
	# 		}
			
	# 		inv_id = self.pool.get('account.invoice').create(cr,uid,inv,context=context)
	# 		inv_line = {
	# 				'name': cb.product_id.name or 'Cashback %s periode %s-%s'%(cb.name.name,cb.start_date,cb.end_date),
	# 				'account_id': expense_account,
	# 				'price_unit': cb.cash_back_amt or 0.0,
	# 				'quantity': 1.0,
	# 				'product_id': cb.product_id and cb.product_id.id or False,
	# 				'uos_id': cb.product_id and cb.product_id.uom_id.id or False,
	# 				'cashback_line_id': cb.id,
	# 				'invoice_id':inv_id,
	# 				}
	# 		self.pool.get('account.invoice.line').create(cr,uid,inv_line)
	# 		cb.write({'invoice_id':inv_id})
	# 		invoice_ids.append(inv_id)
	# 	return True


class account_cashback_line(osv.osv):
	_name = "account.cashback.line"

	def _get_state(self,cr,uid,ids,fields,args,context=None):
		if not context:context={}
		res = {}
		for line in self.browse(cr,uid,ids,context=context):
			res.update({line.id:line.invoice_id and line.invoice_id.status or False}) 
		return {}
	_columns = {
		'name'				: fields.many2one("res.partner","Customer",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		"start_date"		: fields.date("Start Date",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		"end_date"			: fields.date("End Date",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		'current_disc'		: fields.float("Current Disc.",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		'omzet_before_disc'	: fields.float("Omzet B.Disc.",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		'omzet_after_disc'	: fields.float("Omzet A.Disc.",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		'omzet_paid'		: fields.float("Omzet Paid",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		'deposit'			: fields.float("Deposit",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		"proposed_disc"		: fields.float("Proposed Disc.",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		"cash_back_amt"		: fields.float("CashBack Amount",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		"invoice_id"		: fields.many2one("account.invoice","CB. Invoice",readonly=True,states={'draft':[('readonly',False)]}),
		"product_id"		: fields.many2one("product.product","Cash Back Product",readonly=True,states={'draft':[('readonly',False)]}),
		"account_analytic_id": fields.many2one("account.analytic.account","Analytic Account",readonly=True,states={'draft':[('readonly',False)]}),
		"journal_id"		: fields.many2one("account.journal","Journal",readonly=True,states={'draft':[('readonly',False)]}),
		"department_id"		: fields.many2one("account.invoice.department","Department",required=False,readonly=True,states={'draft':[('readonly',False)]}),
		"state"				: fields.selection([('draft','Draft'),('submitted','Submitted'),('approved','Approved'),('done','Done'),('expired','Expired'),('cancelled','Cancelled')],"Status",required=True,readonly=True),
		# "force_cb"			: fields.boolean("Force Rule"),
		# "state"				: fields.function(_get_state,type="selection",selection=[('draft','Draft'),
		# 									('submit','Submit'),
		# 									('approved','Approve'),
		# 									('cancel','Cancelled')],string="State",copy=False,store={
		# 			'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['status'], 50)
		# 		   }),
		"start_date"		: fields.date("Start Date",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		"end_date"			: fields.date("End Date",required=True,readonly=True,states={'draft':[('readonly',False)]}),
		"cashback_id"		: fields.many2one("account.cashback","Cashback",readonly=True,states={'draft':[('readonly',False)]}),
		"date_approved"		: fields.date("Date Approved",readonly=True),
				}
	_order="start_date desc,end_date desc"
	
	_defaults = {
		"state":'draft',
	}



	def update_partner_disc(self,cr,uid,ids,context=None):
		if not context:
			context={}
		partner_disc = self.pool.get("res.partner.discounts")
		for line in self.browse(cr,uid,ids,context=context):
			value = {}
			if line.invoice_id and line.invoice_id.id:
				curr_date = datetime.datetime.strptime(line.end_date,"%Y-%m-%d")
				next_date = curr_date + relativedelta(days=1)
				next_end_date = next_date + relativedelta(months=1)+relativedelta(days=-1)
				cr.execute("select max(coalesce(sequence,0))+1 as sequence from res_partner_discounts where partner_id=%s"%line.name.id)
				sequence = cr.fetchone()

				value = {
					"name" 		: line.proposed_disc or line.name.current_discount or 0.0,
					"start_date": next_date.strftime("%Y-%m-%d"),
					"end_date"	: next_end_date.strftime("%Y-%m-%d"),
					"partner_id": line.name.id,
					"sequence"	: sequence and sequence[0] or 0,
				}
				partner_disc.create(cr,uid,value)
			else:
				continue
		return True

	def delete_zero_omzet(self,cr,uid,ids,partner=False,context=None):
		if not context:context={}
		if context.get('start_date',False) and context.get('end_date',False):
			start_date = context.get('start_date')
			end_date = context.get('end_date')
			query_cashback = """select 
							rp.id,
							before_disc.omzet_before_disc,
							(sum(case when aj.type='sale' then aml.debit else 0.0 END)-sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END)) as omzet_after_disc,
							round(100-((sum(case when aj.type='sale' then aml.debit else 0.0 END)-sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END))/before_disc.omzet_before_disc)*100,2) as disc,
							coalesce(rp.current_discount,0.00) as current_disc,
							sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END) as credit_note,
							sum(case when aml.reconcile_id is not NULL and aml.debit>0.00  then coalesce(rec_aml3.credit,0.00)
								when aml.reconcile_partial_id is not NULL and aml.debit>0.00 then coalesce(rec_aml2.credit,0.00)
								else 0.00
								END) as omzet_paid,
							sum(case when aml.reconcile_id is NULL and aml.reconcile_partial_id is NULL and aml.credit>0.0 and aj.type != 'sale_refund' then coalesce(aml.credit,0.00)
								else 0.00
								END) as deposit
							from account_move_line aml
							left join account_account aa on aml.account_id=aa.id and aa.reconcile=True
							left join account_journal aj on aml.journal_id=aj.id
							left join res_partner rp on aml.partner_id=rp.id
							left join account_period ap on aml.period_id=ap.id
							left join (
								select sum(aml2.credit) as credit,aml2.reconcile_partial_id,aml2.partner_id  
								from account_move_line aml2 
								where aml2.credit>0.0 and aml2.reconcile_partial_id is not NULL 
								and aml2.partner_id in %s
								group by aml2.reconcile_partial_id,aml2.partner_id ) rec_aml2 
								on aml.reconcile_partial_id=rec_aml2.reconcile_partial_id and aml.debit>0.0
							left join (
								select sum(aml3.credit) as credit,aml3.reconcile_id,aml3.partner_id  
								from account_move_line aml3 
								where aml3.credit>0.0 and aml3.reconcile_id is not NULL 
								and aml3.partner_id in %s
								group by aml3.reconcile_id,aml3.partner_id ) rec_aml3 
								on aml.reconcile_id=rec_aml3.reconcile_id and aml.debit>0.0
							left join (
								select ail.partner_id,
									round(sum(
											case 
												when ai.type='out_invoice' and ail.discount=0.0 
													then (100.00/(100.00-rp.current_discount))*(ail.price_unit)*ail.quantity 
												when ai.type='out_invoice' and ail.discount<> 0.0 
													then ail.price_unit*ail.quantity
												when ai.type='out_refund' and ail.discount=0.0
													then (100.00/(100.00-rp.current_discount))*(-1*ail.price_unit)*ail.quantity
												when ai.type='out_refund' and ail.discount<>0.0
													then -1*ail.price_unit*ail.quantity
											end),2) as omzet_before_disc,
									sum(case when ai.type='out_invoice' then ail.price_subtotal else -1*ail.price_subtotal end) as after_disc
									from account_invoice_line ail 
									left join account_invoice ai on ail.invoice_id=ai.id
									left join res_partner rp on ai.partner_id=rp.id
									where  ai.date_invoice >= '%s'
									and ai.date_invoice <= '%s'
									and ai.state in ('open','paid') and ai.type in ('out_invoice','out_refund')
									and ai.partner_id in %s
									group by ail.partner_id
								) before_disc on rp.id=before_disc.partner_id
							where 
							aml.date >= '%s' 
							and aml.date <= '%s'
							and aa.type='receivable' and aa.reconcile=True
							and aml.partner_id is not NULL
							and ap.special=False
							and aj.type in ('sale','sale_refund')
							and before_disc.omzet_before_disc >0.0
							and rp.id in %s
							group by rp.id,rp.current_discount,before_disc.omzet_before_disc
							order by rp.name
							"""%(tuple(partner),tuple(partner),start_date,end_date,tuple(partner),start_date,end_date,tuple(partner))
			cr.execute(query_cashback)
			res =cr.dictfetchall()
			result = {}
			for r in res:
				result.update({r['id']:r})
			to_unlink = []
			for line in self.browse(cr,uid,ids,context=context):
				if not result.get(line.name.id,False):
					to_unlink.append(line.id)
					continue
			self.unlink(cr,uid,to_unlink)
		else:
			for line in self.browse(cr,uid,ids,context=context):
				start_date=line.start_date
				end_date=line.end_date
				dt_line_start = datetime.datetime.strptime(start_date,'%Y-%m-%d')
				dt_line_end = datetime.datetime.strptime(end_date,'%Y-%m-%d')
				query_cashback = """select 
								rp.id,
								before_disc.omzet_before_disc,
								(sum(case when aj.type='sale' then aml.debit else 0.0 END)-sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END)) as omzet_after_disc,
								round(100-((sum(case when aj.type='sale' then aml.debit else 0.0 END)-sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END))/before_disc.omzet_before_disc)*100,2) as disc,
								coalesce(rp.current_discount,0.00) as current_disc,
								sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END) as credit_note,
								sum(case when aml.reconcile_id is not NULL and aml.debit>0.00  then coalesce(rec_aml3.credit,0.00)
									when aml.reconcile_partial_id is not NULL and aml.debit>0.00 then coalesce(rec_aml2.credit,0.00)
									else 0.00
									END) as omzet_paid,
								sum(case when aml.reconcile_id is NULL and aml.reconcile_partial_id is NULL and aml.credit>0.0 and aj.type != 'sale_refund' then coalesce(aml.credit,0.00)
									else 0.00
									END) as deposit
								from account_move_line aml
								left join account_account aa on aml.account_id=aa.id and aa.reconcile=True
								left join account_journal aj on aml.journal_id=aj.id
								left join res_partner rp on aml.partner_id=rp.id
								left join account_period ap on aml.period_id=ap.id
								left join (
									select sum(aml2.credit) as credit,aml2.reconcile_partial_id,aml2.partner_id  
									from account_move_line aml2 
									where aml2.credit>0.0 and aml2.reconcile_partial_id is not NULL
									and aml2.partner_id=%s 
									group by aml2.reconcile_partial_id,aml2.partner_id ) rec_aml2 
									on aml.reconcile_partial_id=rec_aml2.reconcile_partial_id and aml.debit>0.0
								left join (
									select sum(aml3.credit) as credit,aml3.reconcile_id,aml3.partner_id  
									from account_move_line aml3 
									where aml3.credit>0.0 and aml3.reconcile_id is not NULL 
									and aml3.partner_id=%s
									group by aml3.reconcile_id,aml3.partner_id ) rec_aml3 
									on aml.reconcile_id=rec_aml3.reconcile_id and aml.debit>0.0
								left join (
									select ail.partner_id,
									round(sum(
											case 
												when ai.type='out_invoice' and ail.discount=0.0 
													then (100.00/(100.00-rp.current_discount))*(ail.price_unit)*ail.quantity 
												when ai.type='out_invoice' and ail.discount<> 0.0 
													then ail.price_unit*ail.quantity
												when ai.type='out_refund' and ail.discount=0.0
													then (100.00/(100.00-rp.current_discount))*(-1*ail.price_unit)*ail.quantity
												when ai.type='out_refund' and ail.discount<>0.0
													then -1*ail.price_unit*ail.quantity
											end),2) as omzet_before_disc,
									sum(case when ai.type='out_invoice' then ail.price_subtotal else -1*ail.price_subtotal end) as after_disc
									from account_invoice_line ail 
									left join account_invoice ai on ail.invoice_id=ai.id
									left join res_partner rp on ai.partner_id=rp.id
									where  ai.date_invoice >= '%s'
									and ai.date_invoice <= '%s'
									and ai.state in ('open','paid') and ai.type in ('out_invoice','out_refund')
									and ai.partner_id=%s
									group by ail.partner_id
									) before_disc on rp.id=before_disc.partner_id
								where 
								aml.date >= '%s' 
								and aml.date <= '%s'
								and aa.type='receivable' and aa.reconcile=True
								and aml.partner_id is not NULL
								and ap.special=False
								and aml.partner_id=%s
								and aj.type in ('sale','sale_refund')
								and before_disc.omzet_before_disc >0.0
								group by rp.id,rp.current_discount,before_disc.omzet_before_disc
								order by rp.name
							"""%(line.name.id,line.name.id,start_date,end_date,line.name.id,start_date,end_date,line.name.id)
				cr.execute(query_cashback)
				res =cr.dictfetchall()
				result = {}
				for r in res:
					result.update({r['id']:r})
				to_unlink=[]
				for line in self.browse(cr,uid,ids,context=context):
					if not result.get(line.name.id,False):
						to_unlink.append(line.id)
						continue
				self.unlink(cr,uid,to_unlink)
		return True

	def compute_cashback_lines(self,cr,uid,ids,context=None):
		if not context:context={}
		if context.get('start_date',False) and context.get('end_date',False):
			# print "=========ctx============",context
			rule_ids = self.pool.get('account.cashback.rule').search(cr,uid,[('date_start','>=',context.get('start_date',False)),('date_end','<=',context.get('end_date',False))])
			rules = self.pool.get('account.cashback.rule').browse(cr,uid,rule_ids)
			# print "===========",rules
		else:
			rule_ids = self.pool.get('account.cashback.rule').search(cr,uid,[])
			rules = self.pool.get('account.cashback.rule').browse(cr,uid,rule_ids)
		# return True
		if context.get('start_date',False) and context.get('end_date',False):
			start_date = context.get('start_date')
			end_date = context.get('end_date')
			query_cashback = """select 
							rp.id,
							before_disc.omzet_before_disc,
							(sum(case when aj.type='sale' then aml.debit else 0.0 END)-sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END)) as omzet_after_disc,
							round(100-((sum(case when aj.type='sale' then aml.debit else 0.0 END)-sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END))/before_disc.omzet_before_disc)*100,2) as disc,
							coalesce(rp.current_discount,0.00) as current_disc,
							sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END) as credit_note,
							sum(case when aml.reconcile_id is not NULL and aml.debit>0.00  then coalesce(rec_aml3.credit,0.00)
								when aml.reconcile_partial_id is not NULL and aml.debit>0.00 then coalesce(rec_aml2.credit,0.00)
								else 0.00
								END) as omzet_paid,
							sum(case when aml.reconcile_id is NULL and aml.reconcile_partial_id is NULL and aml.credit>0.0 and aj.type != 'sale_refund' then coalesce(aml.credit,0.00)
								else 0.00
								END) as deposit
							from account_move_line aml
							left join account_account aa on aml.account_id=aa.id and aa.reconcile=True
							left join account_journal aj on aml.journal_id=aj.id
							left join res_partner rp on aml.partner_id=rp.id
							left join account_period ap on aml.period_id=ap.id
							left join (
								select sum(aml2.credit) as credit,aml2.reconcile_partial_id,aml2.partner_id  
								from account_move_line aml2 
								where aml2.credit>0.0 and aml2.reconcile_partial_id is not NULL 
								group by aml2.reconcile_partial_id,aml2.partner_id ) rec_aml2 
								on aml.reconcile_partial_id=rec_aml2.reconcile_partial_id and aml.debit>0.0
							left join (
								select sum(aml3.credit) as credit,aml3.reconcile_id,aml3.partner_id  
								from account_move_line aml3 
								where aml3.credit>0.0 and aml3.reconcile_id is not NULL 
								group by aml3.reconcile_id,aml3.partner_id ) rec_aml3 
								on aml.reconcile_id=rec_aml3.reconcile_id and aml.debit>0.0
							left join (
								select ail.partner_id,
									round(sum(
											case 
												when ai.type='out_invoice' and ail.discount=0.0 
													then (100.00/(100.00-rp.current_discount))*(ail.price_unit)*ail.quantity 
												when ai.type='out_invoice' and ail.discount<> 0.0 
													then ail.price_unit*ail.quantity
												when ai.type='out_refund' and ail.discount=0.0
													then (100.00/(100.00-rp.current_discount))*(-1*ail.price_unit)*ail.quantity
												when ai.type='out_refund' and ail.discount<>0.0
													then -1*ail.price_unit*ail.quantity
											end),2) as omzet_before_disc,
									sum(case when ai.type='out_invoice' then ail.price_subtotal else -1*ail.price_subtotal end) as after_disc
									from account_invoice_line ail 
									left join account_invoice ai on ail.invoice_id=ai.id
									left join res_partner rp on ai.partner_id=rp.id
									where  ai.date_invoice >= '%s'
									and ai.date_invoice <= '%s'
									and ai.state in ('open','paid') and ai.type in ('out_invoice','out_refund')
									group by ail.partner_id
								) before_disc on rp.id=before_disc.partner_id
							where 
							aml.date >= '%s' 
							and aml.date <= '%s'
							and aa.type='receivable' and aa.reconcile=True
							and aml.partner_id is not NULL
							and ap.special=False
							and aj.type in ('sale','sale_refund')
							and before_disc.omzet_before_disc >0.0
							group by rp.id,rp.current_discount,before_disc.omzet_before_disc
							order by rp.name
							"""%(start_date,end_date,start_date,end_date)
			cr.execute(query_cashback)
			res =cr.dictfetchall()
			result = {}
			for r in res:
				result.update({r['id']:r})
			for line in self.browse(cr,uid,ids,context=context):
				if not result.get(line.name.id,False):
					line.unlink()
					continue
				current_disc 		= result.get(line.name.id,False) and result[line.name.id]['current_disc'] or 0.0
				omzet_before_disc 	= result.get(line.name.id,False) and result[line.name.id]['omzet_before_disc'] or 0.0
				omzet_after_disc 	= result.get(line.name.id,False) and result[line.name.id]['omzet_after_disc'] or 0.0
				omzet_paid 			= result.get(line.name.id,False) and result[line.name.id]['omzet_paid'] or 0.0
				deposit 			= result.get(line.name.id,False) and result[line.name.id]['deposit'] or 0.0
				product_id			= False
				journal_id			= False
				department_id		= False
				account_analytic_id = False
				cash_back_amt 		= 0.0
				proposed_disc 		= 0.0
				next_disc 			= line.name.current_discount or 0.0
				partner_id 			= line.name and line.name.id
				for rule in rules:

					if eval(rule.rules):
						proposed_disc = rule.next_disc
						product_id = rule.product_id and rule.product_id.id or False
						journal_id = rule.journal_id and rule.journal_id.id
						department_id = rule.department_id and rule.department_id.id
						cash_back_amt = eval(rule.cash_back_amt_rule)
						account_analytic_id = rule.account_analytic_id and rule.account_analytic_id.id or False
						break
				value = {
						'current_disc'		: current_disc,
						'omzet_before_disc'	: omzet_before_disc,
						'omzet_after_disc'	: omzet_after_disc,
						'omzet_paid'		: omzet_paid,
						'deposit'			: deposit,
						'cash_back_amt'		: cash_back_amt,
						'proposed_disc'		: proposed_disc,
						'product_id'		: product_id,
						'journal_id'		: journal_id,
						'department_id'		: department_id,
						'account_analytic_id': account_analytic_id,
						}

				line.write(value)
		else:
			
			for line in self.browse(cr,uid,ids,context=context):
				start_date=line.start_date
				end_date=line.end_date
				dt_line_start = datetime.datetime.strptime(start_date,'%Y-%m-%d')
				dt_line_end = datetime.datetime.strptime(end_date,'%Y-%m-%d')
				query_cashback = """select 
								rp.id,
								before_disc.omzet_before_disc,
								(sum(case when aj.type='sale' then aml.debit else 0.0 END)-sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END)) as omzet_after_disc,
								round(100-((sum(case when aj.type='sale' then aml.debit else 0.0 END)-sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END))/before_disc.omzet_before_disc)*100,2) as disc,
								coalesce(rp.current_discount,0.00) as current_disc,
								sum(case when aj.type ='sale_refund' then aml.credit else 0.00 END) as credit_note,
								sum(case when aml.reconcile_id is not NULL and aml.debit>0.00  then coalesce(rec_aml3.credit,0.00)
									when aml.reconcile_partial_id is not NULL and aml.debit>0.00 then coalesce(rec_aml2.credit,0.00)
									else 0.00
									END) as omzet_paid,
								sum(case when aml.reconcile_id is NULL and aml.reconcile_partial_id is NULL and aml.credit>0.0 and aj.type != 'sale_refund' then coalesce(aml.credit,0.00)
									else 0.00
									END) as deposit
								from account_move_line aml
								left join account_account aa on aml.account_id=aa.id and aa.reconcile=True
								left join account_journal aj on aml.journal_id=aj.id
								left join res_partner rp on aml.partner_id=rp.id
								left join account_period ap on aml.period_id=ap.id
								left join (
									select sum(aml2.credit) as credit,aml2.reconcile_partial_id,aml2.partner_id  
									from account_move_line aml2 
									where aml2.credit>0.0 and aml2.reconcile_partial_id is not NULL 
									group by aml2.reconcile_partial_id,aml2.partner_id ) rec_aml2 
									on aml.reconcile_partial_id=rec_aml2.reconcile_partial_id and aml.debit>0.0
								left join (
									select sum(aml3.credit) as credit,aml3.reconcile_id,aml3.partner_id  
									from account_move_line aml3 
									where aml3.credit>0.0 and aml3.reconcile_id is not NULL 
									group by aml3.reconcile_id,aml3.partner_id ) rec_aml3 
									on aml.reconcile_id=rec_aml3.reconcile_id and aml.debit>0.0
								left join (
									select ail.partner_id,
									round(sum(
											case 
												when ai.type='out_invoice' and ail.discount=0.0 
													then (100.00/(100.00-rp.current_discount))*(ail.price_unit)*ail.quantity 
												when ai.type='out_invoice' and ail.discount<> 0.0 
													then ail.price_unit*ail.quantity
												when ai.type='out_refund' and ail.discount=0.0
													then (100.00/(100.00-rp.current_discount))*(-1*ail.price_unit)*ail.quantity
												when ai.type='out_refund' and ail.discount<>0.0
													then -1*ail.price_unit*ail.quantity
											end),2) as omzet_before_disc,
									sum(case when ai.type='out_invoice' then ail.price_subtotal else -1*ail.price_subtotal end) as after_disc
									from account_invoice_line ail 
									left join account_invoice ai on ail.invoice_id=ai.id
									left join res_partner rp on ai.partner_id=rp.id
									where  ai.date_invoice >= '%s'
									and ai.date_invoice <= '%s'
									and ai.state in ('open','paid') and ai.type in ('out_invoice','out_refund')
									group by ail.partner_id
									) before_disc on rp.id=before_disc.partner_id
								where 
								aml.date >= '%s' 
								and aml.date <= '%s'
								and aa.type='receivable' and aa.reconcile=True
								and aml.partner_id is not NULL
								and ap.special=False
								and aml.partner_id=%s
								and aj.type in ('sale','sale_refund')
								and before_disc.omzet_before_disc >0.0
								group by rp.id,rp.current_discount,before_disc.omzet_before_disc
								order by rp.name
							"""%(start_date,end_date,start_date,end_date,line.name.id)
				cr.execute(query_cashback)
				res =cr.dictfetchall()
				result = {}
				for r in res:
					result.update({r['id']:r})
				current_disc 		= result.get(line.name.id,False) and result[line.name.id]['current_disc'] or 0.0
				omzet_before_disc 	= result.get(line.name.id,False) and result[line.name.id]['omzet_before_disc'] or 0.0
				omzet_after_disc 	= result.get(line.name.id,False) and result[line.name.id]['omzet_after_disc'] or 0.0
				omzet_paid 			= result.get(line.name.id,False) and result[line.name.id]['omzet_paid'] or 0.0
				deposit 			= result.get(line.name.id,False) and result[line.name.id]['deposit'] or 0.0
				product_id			= False
				journal_id			= False
				department_id		= False
				account_analytic_id = False
				cash_back_amt 		= 0.0
				proposed_disc		= 0.0
				next_disc 			= line.name.current_discount or 0.0
				partner_id 			= line.name.id
				for rule in rules:
					dt_start = datetime.datetime.strptime(rule.date_start,'%Y-%m-%d')
					dt_end = datetime.datetime.strptime(rule.date_end,'%Y-%m-%d')
					
					if eval(rule.rules) and (dt_line_start >=dt_start and dt_line_end<=dt_end):
						proposed_disc = rule.next_disc
						print "=================",current_disc,proposed_disc,rule.next_disc
						product_id = rule.product_id and rule.product_id.id
						journal_id = rule.journal_id and rule.journal_id.id
						department_id = rule.department_id and rule.department_id.id
						cash_back_amt = eval(rule.cash_back_amt_rule)
						account_analytic_id = rule.account_analytic_id and rule.account_analytic_id.id or False
						break
				value = {
						'current_disc'		: current_disc,
						'omzet_before_disc'	: omzet_before_disc,
						'omzet_after_disc'	: omzet_after_disc,
						'omzet_paid'		: omzet_paid,
						'deposit'			: deposit,
						'cash_back_amt'		: cash_back_amt,
						'proposed_disc'		: proposed_disc,
						'product_id'		: product_id,
						'journal_id'		: journal_id,
						'department_id'		: department_id,
						'account_analytic_id'		: account_analytic_id,
						}
				line.write(value)
		# print "===================",value
		return True

	# ditambah oleh Andrean 07/12/2017
	# ----------------------------------------------------------------------
	def button_submit(self,cr,uid,ids,context=None):
		self.write(cr, uid, ids, {'state': 'submitted'}, context=context)
		for cbl in self.browse(cr,uid,ids):
			if cbl.cashback_id.state=='draft':
				self.pool.get('account.cashback').write(cr,uid,[cbl.cashback_id.id],{'state':'inprogress'})

		return True

	def button_approve(self,cr,uid,ids,context=None):
		self.write(cr, uid, ids, {'state': 'approved', 'date_approved':datetime.date.today().strftime('%Y-%m-%d')}, context=context)
		return True

	def button_cancel(self,cr,uid,ids,context=None):
		self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
		return True

	def set_to_draft(self,cr,uid,ids,context=None):
		self.write(cr,uid,ids,{'state':'draft'}, context=context)
		return True

	def set_to_expired(self,cr,uid,ids=None,context=None):
		if not ids:
			cr.execute("select id from account_cashback_line where state='approved'")
			ids = [id[0] for id in cr.fetchall()]

		for cbl in self.browse(cr,uid,ids,context=context):
			if cbl.state!='approved': 
				continue

			if ((datetime.date.today()+relativedelta(months=-3)).strftime('%Y-%m-%d'))>cbl.date_approved:
				self.write(cr,uid,ids,{'state':'expired'}, context=context)
		
		return True


	def generate_customer_refund(self,cr,uid,ids,context=None):
		for cb in self.browse(cr,uid,ids,context=context):
			invoice_ids=[]
			account_jrnl_obj = self.pool.get('account.journal')
			invoice_obj = self.pool.get('account.invoice')
			journal_id = account_jrnl_obj.search(cr, uid, [('type', '=', 'sale_refund')], context=None)
			journal_id = journal_id and journal_id[0] or False
			user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
			a = cb.name.property_account_payable.id
			name =cb.cashback_id and cb.cashback_id.name or cb.name.name
			expense_account = cb.product_id.property_account_expense and cb.product_id.property_account_expense.id or \
							cb.product_id.categ_id and cb.product_id.categ_id.property_account_expense_categ and cb.product_id.categ_id.property_account_expense_categ.id or False

			inv = {
				'name': name,
				'origin': name,
				'type': 'out_refund',
				'journal_id': journal_id,
				'reference': cb.name.ref,
				'account_id': a,
				'partner_id': cb.name.id,
				'currency_id': user.company_id.currency_id.id,
				'comment': name,
				'payment_term': cb.name.property_supplier_payment_term and cb.name.property_supplier_payment_term.id or False,
				'fiscal_position': cb.name.property_account_position.id,
				'department_id': cb.department_id and cb.department_id.id,
				'user_id': uid,
				'date_invoice':context.get('date_invoice'),

			}
			inv_id = self.pool.get('account.invoice').create(cr,uid,inv,context=context)

			inv_line = {
					'name': 'Cashback %s periode %s - %s'%(cb.name.name,cb.start_date,cb.end_date),
					'account_id': expense_account,
					'price_unit': cb.cash_back_amt or 0.0,
					'quantity': 1.0,
					'product_id': cb.product_id and cb.product_id.id or False,
					'uos_id': cb.product_id and cb.product_id.uom_id.id or False,
					'cashback_line_id': cb.id,
					'invoice_id':inv_id,
					'account_analytic_id': cb.account_analytic_id and cb.account_analytic_id.id or False,
					}

			self.pool.get('account.invoice.line').create(cr,uid,inv_line)
			cb.write({'invoice_id':inv_id, 'state':'done'})
			invoice = self.pool.get('account.invoice').browse(cr,uid,inv_id,context=context)
			invoice.signal_workflow('invoice_open')

			invoice_ids.append(inv_id)

		return True




	# ---------------------------------------------------------------------------



	def create_invoice(self,cr,uid,ids,context=None):
		if not context:context={}
		context.update({'default_type': 'in_invoice', 'type': 'in_invoice', 'journal_type': 'purchase'})

		account_jrnl_obj = self.pool.get('account.journal')
		invoice_obj = self.pool.get('account.invoice')
		
		journal_id = account_jrnl_obj.search(cr, uid, [('type', '=', 'purchase')], context=None)
		journal_id = journal_id and journal_id[0] or False
		user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
		invoice_ids = []
		
		for line in self.browse(cr,uid,ids,context=context):
			if (line.cash_back_amt==0.0 or (line.omzet_paid<line.omzet_after_disc)) and line.force_cb==False:
				return False
			a = line.name.property_account_payable.id
			name =line.cashback_id and line.cashback_id.name or line.name.name
			expense_account = line.product_id.property_account_expense and line.product_id.property_account_expense.id or \
							line.product_id.categ_id and line.product_id.categ_id.property_account_expense_categ and line.product_id.categ_id.property_account_expense_categ.id or False

			inv = {
				'name': name,
				'origin': name,
				'type': 'in_invoice',
				'journal_id': journal_id,
				'reference': line.name.ref,
				'account_id': a,
				'partner_id': line.name.id,
				'currency_id': user.company_id.currency_id.id,
				'comment': name,
				'payment_term': line.name.property_supplier_payment_term and line.name.property_supplier_payment_term.id or False,
				'fiscal_position': line.name.property_account_position.id,
				'department_id': line.department_id and line.department_id.id,
				'user_id': uid,
			}
			
			inv_id = self.pool.get('account.invoice').create(cr,uid,inv,context=context)
			inv_line = {
					'name': line.product_id.name or 'Cashback %s periode %s-%s'%(line.name.name,line.start_date,line.end_date),
					'account_id': expense_account,
					'price_unit': line.cash_back_amt or 0.0,
					'quantity': 1.0,
					'product_id': line.product_id and line.product_id.id or False,
					'uos_id': line.product_id and line.product_id.uom_id.id or False,
					'cashback_line_id': line.id,
					'invoice_id':inv_id,
					'account_analytic_id':line.account_analytic_id and line.account_analytic_id.id or False,
					}
			self.pool.get('account.invoice.line').create(cr,uid,inv_line)
			line.write({'invoice_id':inv_id})
			invoice_ids.append(inv_id)
		return True

class account_invoice_line(osv.osv):
	_inherit = "account.invoice.line"
	_columns = {
	"cashback_line_id" : fields.many2one("account.cashback.line","Cashback Line"),
	}

class account_invoice(osv.osv):
	_inherit = "account.invoice"

	_columns = {
		"cashback_ids": fields.one2many('account.cashback.line','invoice_id',"Cashback Line")
	}