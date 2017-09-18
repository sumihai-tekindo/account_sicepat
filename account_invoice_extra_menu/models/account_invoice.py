from openerp.osv import osv,fields
from openerp.report import report_sxw
from datetime import datetime

class account_invoice(osv.osv):
	_inherit = "account.invoice"

	_columns = {
		"followup_user_id" : fields.related('partner_id', 'payment_responsible_id', type='many2one', relation='res.users', string='Follow-up Responsible', store=True, readonly=True,),
	}


class account_invoice_collection(osv.osv_memory):
	_name = "account.invoice.collection"

	_columns = {
	"name" : fields.text("Notes"),
	}

	def default_get(self,cr,uid,fields,context=None):
		res = super(account_invoice_collection,self).default_get(cr,uid,fields,context=context)

		# acc_ids = self.pool.get('account.account').search(cr,uid,ids,context=None)
		# account = self.pool.get('account.account').search(cr,uid,ids,context=context)
		invoice_ids = context.get('active_ids',False)
		rml_parser = report_sxw.rml_parse(cr, uid, 'reconciliation_widget_aml', context=context)
		if invoice_ids and context.get('active_model',False)=='account.invoice':
			invoices = self.pool.get('account.invoice').browse(cr,uid,invoice_ids,context=context)
			cust = []
			total_unpaid = 0.0
			text = "%s \n"%(invoices and invoices[0] and invoices[0].partner_id and invoices[0].partner_id.name)
			receivable_dict = {}
			for inv in invoices:
				for acc in inv.company_id.receivable_ids:
					key = acc.id
					if receivable_dict.get(key):
						if acc.id!=inv.account_id.id:
							continue
						receivable_dict[key]['line']+=inv
						receivable_dict[key]['total']+=inv.residual
					else:
						if acc.id!=inv.account_id.id:
							continue
						receivable_dict[key]={
							'name':acc.name,
							'line':inv,
							'total':inv.residual,
							'currency_id':inv.currency_id}

			for k,v in sorted(receivable_dict.items()):
				for line in v['line']:
					text += "%s %s\n"%(line.date_invoice,rml_parser.formatLang(line.residual, currency_obj=line.currency_id))
				
				total_unpaid+=v['total']
				text+="\nSubTotal %s : %s\n\n\n"%(v['name'],rml_parser.formatLang(v['total'], currency_obj=v['currency_id']))

			text+="Total : %s\n\n\n"%(rml_parser.formatLang(total_unpaid))

			# 		if acc.id == 'Piutang Usaha':
			# 			cust.append(inv.partner_id and inv.partner_id.id)
			# 			total_unpaid += inv.residual or 0.0
			# 			text += "%s %s\n"%(inv.date_invoice,rml_parser.formatLang(inv.residual, currency_obj=inv.currency_id))
			# 		if inv.account_id.name == 'Piutang Cargo':
			# 			cust.append(inv.partner_id and inv.partner_id.id)
			# 			total_unpaid_cargo += inv.residual or 0.0
			# 			text += "%s %s\n"%(inv.date_invoice,rml_parser.formatLang(inv.residual, currency_obj=inv.currency_id))
			# text+="\nSubTotal : %s\n"%(rml_parser.formatLang(total_unpaid, currency_obj=inv.currency_id))
			# text+="Subtotal Cargo: %s\n\n"%(rml_parser.formatLang(total_unpaid_cargo, currency_obj=inv.currency_id))



			cb_model, journal_id = self.pool.get('ir.model.data').get_object_reference(cr, uid,'account_cash_back','cash_back_journal')

			unreconciled_payment = [('partner_id','=',inv.partner_id and inv.partner_id.id),('reconcile_id','=',False),('account_id.type','=','receivable'),('credit','>',0.0),('journal_id','!=',journal_id)]
			aml_ids = self.pool.get('account.move.line').search(cr,uid,unreconciled_payment)

			unreconciled=0.0
			if aml_ids:
				amls = self.pool.get('account.move.line').browse(cr,uid,aml_ids)
				for aml in amls :
					if aml.amount_residual>0.0:
					
						unreconciled+= aml.amount_residual
					# unreconciled+= aml.amount_residual
				text+="Lebih bayar : %s\n"%(rml_parser.formatLang(abs(unreconciled), currency_obj=inv.currency_id))


			cashback_amt = 0.0
			cbl_ids = self.pool.get('account.cashback.line').search(cr,uid,[('name','=',inv.partner_id.id),('state','=','approved')])
			cbl = self.pool.get('account.cashback.line').browse(cr,uid,cbl_ids,context=context)
			for cashback in cbl :
				cashback_amt+=cashback.cash_back_amt
			
			unreconciled_payment = [('partner_id','=',inv.partner_id and inv.partner_id.id),('reconcile_id','=',False),('account_id.type','=','receivable'),('credit','>',0.0),('journal_id','=',journal_id)]
			aml_ids = self.pool.get('account.move.line').search(cr,uid,unreconciled_payment)

			if aml_ids:
				amls = self.pool.get('account.move.line').browse(cr,uid,aml_ids)
				for aml in amls :
					if aml.amount_residual>0.0:
					
						cashback_amt+= aml.amount_residual

			text+="Cashback : %s"%(rml_parser.formatLang(abs(cashback_amt), currency_obj=inv.currency_id))


			text+="\nTotal : %s\n"%(rml_parser.formatLang((total_unpaid-abs(unreconciled)-abs(cashback_amt)), currency_obj=inv.currency_id))
			text+="\nPembayaran dapat melalui : \n\nBANK BCA \nNO rekening : 270 390 3088 \nAtas Nama: Sicepat Ekspres Indonesia\n\nBANK MANDIRI \nNO rekening : 121 000 655 7171 \nAtas Nama : Sicepat Ekspres Indonesia\n\nBANK BNI \nNO rekening : 4964 66952\nAtas Nama : Sicepat Ekspres Indonesia\n\nBANK BRI \nNO rekening : 0338 01 001027 30 7\nAtas Nama : Sicepat Ekspres Indonesia"
			text+="\n\nHarap isi berita acara nama OLSHOP dan tanggal pengiriman di berita acara.\nContoh: 'SiCepatShop 19Feb15'"
		
		elif invoice_ids and context.get('active_model',False)=='account.move.line':
			invoices = self.pool.get('account.move.line').browse(cr,uid,invoice_ids,context=context)

			cust = []
			total_unpaid = 0.0
			total_unpaid_cargo = 0.0  #tambahin cargo   
			text = "%s \n"%(invoices and invoices[0] and invoices[0].partner_id and invoices[0].partner_id.name)
			import locale
			import re
			receivable_dict = {}
			for inv in invoices:
				if inv.invoice and inv.invoice.cashback_ids and inv.invoice.cashback_ids != [] :
					continue
				for acc in inv.company_id.receivable_ids:
					key = acc.id
					if receivable_dict.get(key):
						if acc.id!=inv.account_id.id:
							continue
						receivable_dict[key]['line']+=inv
						receivable_dict[key]['total']+=inv.amount_residual
					else:
						if acc.id!=inv.account_id.id:
							continue
						receivable_dict[key]={
							'name':acc.name,
							'line':inv,
							'total':inv.amount_residual,
							'currency_id':inv.currency_id or inv.company_id.currency_id}
				# cust.append(inv.partner_id and inv.partner_id.id)
				# total_unpaid += inv.amount_residual or 0.0
				# # print "=================",inv.amount_residual,total_unpaid
				# result = re.findall("(\d\d)\-(.*?)\-(\w+)",inv.name)
				# substring=False
				# if result and result[0]:
				# 	substring=result[0][0]+"-"+result[0][1]+"-"+result[0][2]

				# subst_date = False
				try:
					try:
						try:
							locale.setlocale(locale.LC_TIME,"id_ID.UTF-8")
							subst_date = datetime.strptime(substring,'%d-%b-%y')
						except:
							locale.setlocale(locale.LC_TIME,"en_US.UTF-8")
							subst_date = datetime.strptime(substring,'%d-%b-%y')
					except:
						locale.setlocale(locale.LC_TIME,"en_US.UTF-8")
						subst_date = datetime.strptime(substring,'%d-%m-%Y')
					locale.setlocale(locale.LC_TIME,"en_US.UTF-8")
				except:
					subst_date=False
				inv_date = datetime.strptime(inv.date,'%Y-%m-%d')

				if subst_date and subst_date != inv_date:
					inv_date = subst_date
				inv_date=datetime.strftime(inv_date,'%Y-%m-%d')

			for k,v in sorted(receivable_dict.items()):
				for line in v['line']:
					text += "%s %s\n"%(line.date,rml_parser.formatLang(line.amount_residual, currency_obj=line.currency_id))

				total_unpaid+=v['total']	
				text+="\nSubTotal %s : %s\n\n\n"%(v['name'],rml_parser.formatLang(v['total'], currency_obj=v['currency_id']))
			
			text+="Total : %s\n\n\n"%(rml_parser.formatLang(total_unpaid))
			# 	text += "%s %s\n"%(inv_date,rml_parser.formatLang(inv.amount_residual, currency_obj=inv.currency_id or inv.company_id.currency_id))
			# text+="\nSubTotal : %s\n"%(rml_parser.formatLang(total_unpaid, currency_obj=inv.currency_id or inv.company_id.currency_id))



			unreconciled_payment = [('partner_id','=',inv.partner_id and inv.partner_id.id),('reconcile_id','=',False),('account_id.type','=','receivable'),('credit','>',0.0)]
			aml_ids = self.pool.get('account.move.line').search(cr,uid,unreconciled_payment)

			unreconciled=0.0
			if aml_ids:
				amls = self.pool.get('account.move.line').browse(cr,uid,aml_ids)
				for aml in amls :
					if aml.amount_residual>0.0:
						
						unreconciled+= aml.amount_residual
				text+="Lebih bayar : %s\n"%(rml_parser.formatLang(abs(unreconciled), currency_obj=inv.currency_id or inv.company_id.currency_id))


			cashback_amt = 0.0
			cbl_ids = self.pool.get('account.cashback.line').search(cr,uid,[('name','=',inv.partner_id.id),('state','=','approved')])
			cbl = self.pool.get('account.cashback.line').browse(cr,uid,cbl_ids,context=context)
			for cashback in cbl :
				cashback_amt+=cashback.cash_back_amt
			text+="Cashback : %s"%(rml_parser.formatLang(abs(cashback_amt), currency_obj=inv.currency_id or inv.company_id.currency_id))


			text+="\nTotal : %s\n"%(rml_parser.formatLang((total_unpaid-abs(unreconciled)-abs(cashback_amt)), currency_obj=inv.currency_id or inv.company_id.currency_id))
			text+="\nPembayaran dapat melalui : \n\nBANK BCA \nNO rekening : 270 390 3088 \nAtas Nama: Sicepat Ekspres Indonesia\n\nBANK MANDIRI \nNO rekening : 121 000 655 7171 \nAtas Nama : Sicepat Ekspres Indonesia\n\nBANK BNI \nNO rekening : 4964 66952\nAtas Nama : Sicepat Ekspres Indonesia\n\nBANK BRI \nNO rekening : 0338 01 001027 30 7\nAtas Nama : Sicepat Ekspres Indonesia"
			text+="\n\nHarap isi berita acara nama OLSHOP dan tanggal pengiriman di berita acara.\nContoh: 'SiCepatShop 19Feb15'"

		res.update({
			'name': text,
		})
		return res