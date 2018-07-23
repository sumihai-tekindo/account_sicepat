from openerp.osv import fields, osv

class accounting_report(osv.osv_memory):
	_inherit = "accounting.report"

	_columns = {
		'with_difference': fields.boolean("Print Difference"),
		'with_total': fields.boolean("Print Total"),
		'group_by': fields.selection([('none', 'None'), ('department', 'Department'), ('analytic', 'Analytic')], "Group by", required=True),
		'all_department': fields.boolean('All Departments?'),
		'department_ids': fields.many2many('account.invoice.department', 'report_account_department_rel', 'did', 'rid',  string='Departments'),
		'all_analytic': fields.boolean('All Account Analytics?'),
		'analytic_ids': fields.many2many('account.analytic.account', 'report_account_analytic_rel', 'aid', 'rid', string='Analytic Accounts',
				domain=[('tag', 'in', ('gerai', 'cabang', 'toko', 'head_office', 'agen', 'transit', 'pusat_transitan')), ('parent_id.tag', '=', 'kota')]),
		'report_type': fields.selection([
			('xlsx','XLSX'),
			('pdf','PDF')
			], 'Report Type', required=True),
	}
	_defaults = {
		'group_by': 'none',
		'all_department': True,
		'all_analytic': True,
		'report_type': 'xlsx',
	}

	def _print_report(self, cr, uid, ids, data, context=None):
		data['form'].update(self.read(cr, uid, ids, ['date_from_cmp',  'debit_credit', 'date_to_cmp',  'fiscalyear_id_cmp', 'period_from_cmp', 'period_to_cmp',  'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move', 'with_difference', 'with_total', 'group_by', 'all_department', 'department_ids', 'all_analytic', 'analytic_ids', 'report_type'], context=context)[0])
		if data['form']['report_type'] == 'xlsx':
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'account.report_financial_xlsx',
				'datas': data,
				'data': data,
			}
		return self.pool['report'].get_action(cr, uid, [], 'account.report_financial', data=data, context=context)

