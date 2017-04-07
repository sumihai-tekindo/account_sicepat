from openerp.osv import fields,osv
import datetime


class account_move_line_statement_wiz(osv.osv_memory):
	_name = "account.move.line.statement"
	_columns  = {
		"name"					: fields.many2one("account.journal","Bank",required=True),
		"payment_date"			: fields.date("Payment Date"),
		"move_line_ids"			: fields.many2many("account.move.line","account_move_line_statement_rel","statement_id","move_line_id","Journal Items"),
		"into_existing"			: fields.boolean("Import into existing?"),
		"statement_id"			: fields.many2one("account.bank.statement","Existing Bank Statement"),
		"reconcile"				: fields.boolean("Auto reconcile"),
	}

	_defaults = {
		"reconcile": True,
	}
	def default_get(self,cr,uid,fields,context=None):
		res = super(account_move_line_statement_wiz,self).default_get(cr,uid,fields,context=context)
		move_line_ids = context.get('active_ids',False)
		if move_line_ids:
			
			res.update({
				'move_line_ids': move_line_ids,
			})
		return res

	def generate_bank_statement(self,cr,uid,ids,context=None):
		if not context:context={}
		data = self.browse(cr, uid, ids, context=context)[0]
		print ""
		line_ids = data.move_line_ids
		if not line_ids:
			return {'type': 'ir.actions.act_window_close'}
		mod_obj = self.pool.get('ir.model.data')
		period_pool = self.pool.get('account.period')
		line_obj = self.pool.get('account.move.line')
		statement_obj = self.pool.get('account.bank.statement')
		statement_line_obj = self.pool.get('account.bank.statement.line')
		currency_obj = self.pool.get('res.currency')
		act_obj = self.pool.get('ir.actions.act_window')
		payment_date = data.payment_date or datetime.date.today().strftime('%Y-%m-%d')
		period_id = period_pool.find(cr, uid, dt=payment_date, context=context)
		company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.bank.statement',context=context)
		if not data.into_existing:
			statement_value = {
				'name':'/',
				'date':payment_date,
				'journal_id':data.name and data.name.id,
				'period_id': period_id and period_id[0] or False,
				'company_id': company_id,
				'state':'draft'
			}
			statement_id = statement_obj.create(cr,uid,statement_value)
		else:
			statement_id = data.statement_id and data.statement_id.id or False
		statement = statement_obj.browse(cr, uid, statement_id, context=context)
		line_date = statement.date
		# for each selected move lines
		for line in line_ids:
			if line.statement_recon_id and line.statement_recon_id.id:
				inv_name = line.invoice and line.invoice.number or line.ref
				raise osv.except_osv(_('Error!'),_("This line %s already exists in statement %s"%(inv_name,line.statement_recon_id.name)))
			ctx = context.copy()
			#  take the date for computation of currency => use payment date
			ctx['date'] = line_date
			amount = 0.0

			if line.debit > 0:
				amount = line.debit
			elif line.credit > 0:
				amount = -line.credit

			if line.amount_currency:
				if line.company_id.currency_id.id != statement.currency.id:
					# In the specific case where the company currency and the statement currency are the same
					# the debit/credit field already contains the amount in the right currency.
					# We therefore avoid to re-convert the amount in the currency, to prevent Gain/loss exchanges
					amount = currency_obj.compute(cr, uid, line.currency_id.id,
						statement.currency.id, line.amount_currency, context=ctx)
			elif (line.invoice and line.invoice.currency_id.id != statement.currency.id):
				amount = currency_obj.compute(cr, uid, line.invoice.currency_id.id,
					statement.currency.id, amount, context=ctx)

			context.update({'move_line_ids': [line.id],
							'invoice_id': line.invoice.id})

			st_line_id = statement_line_obj.create(cr, uid, {
					'name': line.name or '?',
					'amount': amount,
					'partner_id': line.partner_id.id,
					'statement_id': statement_id,
					'ref': line.ref,
					'date': payment_date,
					'amount_currency': line.amount_currency,
					'currency_id': line.currency_id.id,
				}, context=context)
			if data.reconcile:
				st_line = statement_line_obj.browse(cr, uid, [st_line_id], context=context)
				reconciliation_proposition = statement_line_obj.get_reconciliation_proposition(cr, uid, st_line, context=context)
				if reconciliation_proposition:
					mv_line_dict = {
						'debit': reconciliation_proposition[0]['credit'],
						'credit': reconciliation_proposition[0]['debit'],
						'name': reconciliation_proposition[0]['name'],
						'counterpart_move_line_id': reconciliation_proposition[0]['id'],
					}
					statement_line_obj.process_reconciliation(cr, uid, st_line_id, [mv_line_dict], context=context)
		self.pool.get('account.move.line').write(cr,uid,[x.id for x in line_ids],{'statement_recon_id':statement_id})
		result = mod_obj.get_object_reference(cr, uid, 'account', 'action_bank_statement_tree')
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		result['domain'] = "[('id','in', [" + ','.join(map(str, [statement_id])) + "])]"

		return result

class account_move_line(osv.osv):
	_inherit="account.move.line"

	_columns = {
		"statement_recon_id"	: fields.many2one("account.bank.statement","Bank Statement", ondelete='set null'),
	}