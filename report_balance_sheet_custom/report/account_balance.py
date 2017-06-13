from openerp.addons.account.report.account_balance import account_balance
from openerp.tools.translate import _
from openerp.osv import osv
import time
from openerp.report import report_sxw

class account_balance_inh(account_balance):
	_inherit = 'report.account.account.balance'

	def __init__(self, cr, uid, name, context=None):
		super(account_balance_inh, self).__init__(cr, uid, name, context=context)
		self.initial_balance = False
		self.sum_initial = 0.0
		self.localcontext.update({
			'lines': self.lines,
		})
		self.context = context

	def lines(self, form, ids=None, done=None):
		self.initial_balance = form.get('initial_balance',False)

		def _process_child(accounts, disp_acc, parent):
				account_rec = [acct for acct in accounts if acct['id']==parent][0]
				currency_obj = self.pool.get('res.currency')
				acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
				currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
				res = {
					'id': account_rec['id'],
					'type': account_rec['type'],
					'code': account_rec['code'],
					'name': account_rec['name'],
					'level': account_rec['level'],
					'debit': account_rec['debit'],
					'credit': account_rec['credit'],
					'balance': account_rec['balance'],
					'parent_id': account_rec['parent_id'],
					'bal_type': '',
				}

				if self.initial_balance:
					acc_id_init = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'],context = ctx_2)
					
					res.update({'initial_bal':acc_id_init.balance})
					self.sum_initial+=acc_id_init.balance

				self.sum_debit += account_rec['debit']
				self.sum_credit += account_rec['credit']
				if disp_acc == 'movement':
					if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
						self.result_acc.append(res)
				elif disp_acc == 'not_zero':
					if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
						self.result_acc.append(res)
				else:
					self.result_acc.append(res)
				if account_rec['child_id']:
					for child in account_rec['child_id']:
						_process_child(accounts,disp_acc,child)

		obj_account = self.pool.get('account.account')
		if not ids:
			ids = self.ids
		if not ids:
			return []
		if not done:
			done={}

		ctx = self.context.copy()

		ctx['fiscalyear'] = form['fiscalyear_id']
		if form['filter'] == 'filter_period':
			ctx['period_from'] = form['period_from']
			ctx['period_to'] = form['period_to']
		elif form['filter'] == 'filter_date':
			ctx['date_from'] = form['date_from']
			ctx['date_to'] =  form['date_to']

		ctx['state'] = form['target_move']
		if self.initial_balance:
			ctx_2 =ctx.copy()
			periods =  self.pool["account.period"].build_ctx_periods(self.cr, self.uid, form['period_from'], form['period_to'])
			ctx_2.update({'initial_bal':self.initial_balance,'periods':periods})
		parents = ids
		child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
		if child_ids:
			ids = child_ids
		accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)

		for parent in parents:
				if parent in done:
					continue
				done[parent] = 1
				_process_child(accounts,form['display_account'],parent)
		return self.result_acc


class report_trialbalance(osv.AbstractModel):
	_name = 'report.account.report_trialbalance'
	_inherit = 'report.abstract_report'
	_template = 'account.report_trialbalance'
	_wrapped_report_class = account_balance_inh