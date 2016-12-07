from openerp.osv import osv,fields


class account_invoice(osv.osv):
	_inherit = "account.invoice"

	_columns = {
		"followup_user_id" : fields.related('partner_id', 'payment_responsible_id', type='many2one', relation='res.users', string='Follow-up Responsible', store=True, readonly=True,),
	}