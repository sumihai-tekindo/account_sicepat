from openerp.osv import fields,osv

class bank_statement_validate_wiz(osv.osv_memory):
	_name = "bank.statement.validate.wiz"

	def open_close_bank_statement(self,cr,uid,ids,context=None):
		if not context:context={}
		
		action_button = context.get('action_button',False)
		bs_ids = context.get('active_ids',False)
		bss = []
		if action_button and action_button=='open':
			for bs in self.pool.get('account.bank.statement').browse(cr,uid,bs_ids,context=context):
				if bs.state=='draft':
					bss.append(bs.id)
			self.pool.get("account.bank.statement").button_open(cr, uid, bss, context=context)
		elif action_button and action_button=='close':
			for bs in self.pool.get('account.bank.statement').browse(cr,uid,bs_ids,context=context):
				if bs.state=='open':
					bss.append(bs.id)
			self.pool.get("account.bank.statement").button_confirm_cash(cr,uid,bss,context=context)
		return {'type': 'ir.actions.act_window_close'}