from openerp.osv import fields, osv

class accounting_report(osv.osv_memory):
	_inherit = "accounting.report"

	_columns = {
		'with_difference': fields.boolean("Print Difference"),
		'with_total'	 : fields.boolean("Print Total"),
		'report_type': fields.selection([
			('xlsx','XLSX'),
			('pdf','PDF')
			], 'Report Type', required=True),
	}
	_defaults = {
		'report_type': 'xlsx',
	}

	def _print_report(self, cr, uid, ids, data, context=None):
		data['form'].update(self.read(cr, uid, ids, ['date_from_cmp',  'debit_credit', 'date_to_cmp',  'fiscalyear_id_cmp', 'period_from_cmp', 'period_to_cmp',  'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter','target_move','with_difference','with_total','report_type'], context=context)[0])
		if data['form']['report_type'] == 'xlsx':
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'account.report_financial_xlsx',
					'datas': data,
					'data': data,
				}
		return self.pool['report'].get_action(cr, uid, [], 'account.report_financial', data=data, context=context)

