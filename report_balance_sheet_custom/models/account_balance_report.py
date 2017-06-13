
from openerp.osv import fields, osv


class account_balance_report(osv.osv_memory):
	_inherit = "account.balance.report"

	_columns = {
		'initial_balance': fields.boolean('Include Initial Balances',
									help='If you selected to filter by date or period, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.'),
	}


	def check_report(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		res = super(account_balance_report, self).check_report(cr, uid, ids, context=context)

		
		wiz = self.browse(cr, uid, ids, context=context)[0]
		res['data']['form']['initial_balance'] = wiz.initial_balance
		return res

	def _print_report(self, cr, uid, ids, data, context=None):
		data = self.pre_print_report(cr, uid, ids, data, context=context)
		wiz = self.browse(cr, uid, ids)
		data['form'].update({'initial_balance': wiz.initial_balance})
		return self.pool['report'].get_action(cr, uid, [], 'account.report_trialbalance', data=data, context=context)