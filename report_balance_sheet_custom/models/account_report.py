from openerp.osv import fields, osv
import time







class accounting_report(osv.osv_memory):
	_inherit = "accounting.report"

	_columns = {
		'with_difference': fields.boolean("Print Difference"),
		'with_total'	 : fields.boolean("Print Total"),
	}

	def check_report(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		res = super(accounting_report, self).check_report(cr, uid, ids, context=context)

		data = {}
		data['form'] = self.read(cr, uid, ids, ['account_report_id', 'date_from_cmp',  'date_to_cmp',  'fiscalyear_id_cmp', 'journal_ids', 'period_from_cmp', 'period_to_cmp',  'filter_cmp',  'chart_account_id', 'target_move','with_difference','with_total'], context=context)[0]
		for field in ['fiscalyear_id_cmp', 'chart_account_id', 'period_from_cmp', 'period_to_cmp', 'account_report_id']:
			if isinstance(data['form'][field], tuple):
				data['form'][field] = data['form'][field][0]
		comparison_context = self._build_comparison_context(cr, uid, ids, data, context=context)
		dxdiag = self.browse(cr,uid,ids,context=context)
		res['data']['form']['comparison_context'] = comparison_context
		res['data']['form']['with_difference'] = dxdiag.with_difference
		res['data']['form']['with_total'] = dxdiag.with_total
		return res


