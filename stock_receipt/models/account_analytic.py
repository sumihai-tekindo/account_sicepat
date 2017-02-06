from openerp.osv import osv, fields

class account_analytic_account(osv.osv):
	_inherit = "account.analytic.account"

	_columns ={
		"user_admin_id" : fields.many2one("hr.employee","User Admin"),
		"day_interval"	: fields.float("Interval for sending goods(days)"),
	}
