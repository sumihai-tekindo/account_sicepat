from openerp.osv import osv,fields
from openerp.report import report_sxw


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
		invoice_ids = context.get('active_ids',False)
		rml_parser = report_sxw.rml_parse(cr, uid, 'reconciliation_widget_aml', context=context)
		if invoice_ids:
			invoices = self.pool.get('account.invoice').browse(cr,uid,invoice_ids,context=context)
			cust = []
			total_unpaid = 0.0
			text = "%s \n"%(invoices and invoices[0] and invoices[0].partner_id and invoices[0].partner_id.name)
			for inv in invoices:
				cust.append(inv.partner_id and inv.partner_id.id)
				total_unpaid += inv.residual or 0.0
				text += "%s %s\n"%(inv.date_invoice,rml_parser.formatLang(inv.residual, currency_obj=inv.currency_id))
			text+="\nSubTotal : %s\n"%(rml_parser.formatLang(total_unpaid, currency_obj=inv.currency_id))

			unreconciled_payment = [('partner_id','=',inv.partner_id and inv.partner_id.id),('reconcile_id','=',False),('account_id.type','=','receivable'),('credit','>',0.0)]
			aml_ids = self.pool.get('account.move.line').search(cr,uid,unreconciled_payment)

			unreconciled=0.0
			if aml_ids:
				amls = self.pool.get('account.move.line').browse(cr,uid,aml_ids)
				for aml in amls :
					unreconciled+= aml.amount_residual
				text+="Lebih bayar : %s"%(rml_parser.formatLang(abs(unreconciled), currency_obj=inv.currency_id))
			text+="\nTotal : %s\n"%(rml_parser.formatLang((total_unpaid-abs(unreconciled)), currency_obj=inv.currency_id))
			text+="\nPembayaran dapat melalui : \n\nBANK BCA \nNO rekening : 270 390 3088 \nAtas Nama: Sicepat Ekspres Indonesia\n\nBANK MANDIRI \nNO rekening : 121 000 655 7171 \nAtas Nama : Sicepat Ekspres Indonesia"
			text+="\n\nHarap isi berita acara nama OLSHOP dan tanggal pengiriman di berita acara.\nContoh: 'SiCepatShop 19Feb15'"
		res.update({
			'name': text,
		})
		return res