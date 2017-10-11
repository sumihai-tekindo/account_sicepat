from openerp.osv import osv,fields

class account_journal(osv.osv):
	_inherit = "account.journal"
	_columns = {
		"cb_journal": fields.boolean("Cashback Journal",help="Check this fields if it is used as cashback journal"),
		"compute_as_cb": fields.boolean("Computed in cashback",help="Check this fields if it is computed in cashback"),
	}
