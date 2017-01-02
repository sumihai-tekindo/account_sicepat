from openerp.osv import fields,osv

class account_move_line(osv.osv):
	_inherit="account.move.line"
	_columns = {
		"followup_user_id" : fields.related('partner_id', 'payment_responsible_id', type='many2one', 
			relation='res.users', string='Follow-up Responsible', store=True, readonly=True,),
	}