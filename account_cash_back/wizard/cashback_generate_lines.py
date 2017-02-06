from openerp.osv import fields,osv

class cashback_lines_wizard(osv.osv_memory):
	_name = "cashback.lines.wizard"

	_columns = {
	"customer_ids"			: fields.many2many('res.partner', 'cashback_lines_wizard_partner_rel', 'wiz_id', 'partner_id', 'Customers',),
	"cashback_id"			: fields.many2one('account.cashback',"Cashback"),
	"current_customer_ids"	: fields.many2many('res.partner', 'cashback_lines_current_partner_rel', 'wiz_id', 'partner_id', 'Existing Customers',),
	"start_date"			: fields.date("Start Date",required=True),
	"end_date"				: fields.date("End Date",required=True),
	}

	def default_get(self,cr,uid,fields,context=None):
		res = super(cashback_lines_wizard,self).default_get(cr,uid,fields,context=context)
		if context.get('active_id',False):
			cashback = self.pool.get('account.cashback').browse(cr,uid,context.get('active_id'))
			current_customer_ids = [x.name and x.name.id for x in cashback.line_ids]
		res.update({
			'cashback_id': context.get('active_id',False),
			'current_customer_ids' : current_customer_ids,
			'start_date': cashback.start_date,
			'end_date':cashback.end_date,
		})
		return res



	def generate(self,cr,uid,ids,context=None):
		if not context:context={}
		wiz = self.browse(cr,uid,ids[0],context=context)
		for partner in wiz.customer_ids:
			value = {
				"name":partner and partner.id,
				"start_date":wiz.start_date,
				"end_date"	:wiz.end_date,
				"current_disc":partner.current_discount or 0.0,
				"cashback_id":wiz.cashback_id and wiz.cashback_id.id or False,
				"omzet_before_disc":0.0,
				"omzet_after_disc":0.0,
				"omzet_paid":0.0,
				"deposit":0.0,
				"proposed_disc":0.0,
				"cash_back_amt":0.0,
				}
			print "xxxxxxxxxxxxxxxxx",value
			self.pool.get('account.cashback.line').create(cr,uid,value)
		return True