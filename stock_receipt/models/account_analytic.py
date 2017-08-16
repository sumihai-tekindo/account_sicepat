from openerp.osv import osv, fields

class account_analytic_account(osv.osv):
	_inherit = "account.analytic.account"

	_columns ={
		"user_admin_id" : fields.many2one("res.users","User Admin"),
		"day_interval"	: fields.float("Interval for sending goods(days)"),
		'koordinator_regional' : fields.many2one('hr.employee', 'Koordinator Regional', required=True),
		'koordinator_wilayah' :fields.many2one('hr.employee', 'Koordinator Wilayah', required=True),
		'koordinator_ops_malam' : fields.many2one('hr.employee', 'Koordinator OPS Malam'),
		'koordinator_pickup' : fields.many2one('hr.employee', 'Koordinator Pickup'),
		'koordinator_antar' : fields.many2one('hr.employee', 'Koordinator Antar', required=True),
	}
