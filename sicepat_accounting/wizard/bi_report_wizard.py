from openerp.osv import fields,osv

class bi_report_wizard(osv.osv_memory):
	_name = "bi.report.wizard"

	_columns = {
	"report_type"	: fields.selection(
		[
		('revenue_package','Revenue and Package'),
		('revenue_toko','Revenue Toko'),
		('revenue_gerai','Revenue per Gerai'),
		('revenue_perwakilan','Revenue per Perwakilan'),
		],"Jenis Laporan",required=True),

	"start_date"	: fields.date("Start Date" ,required=True),
	"end_date"		: fields.date("End Date" ,required=True),
	}

	_defaults = {
		"report_type":'revenue_package',
	}

	def print_report(self,cr,uid,ids,context=None):
		if not context:context={}
		wiz = self.browse(cr,uid,ids,context=context)[0]
		datas = {
            'model': 'account.move.line',
            'start_date': wiz.start_date or False,
            'end_date': wiz.end_date or False,
			'ids': False,
			'account_ids':wiz.account_ids and [x.id for x in wiz.account_ids] or False,
			't_report': wiz.report_type,
			}
		if wiz.report_type=='revenue_package':
			move_ids = self.pool.get('account.move.line').search(cr,uid,[],limit=1)
			datas.update({'ids':move_ids})
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'revenue.package',
					'datas': datas
					}
		elif wiz.report_type=='revenue_toko':
			move_ids = self.pool.get('account.move.line').search(cr,uid,[],limit=1)
			datas.update({'ids':move_ids})
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'revenue.package',
					'datas': datas
					}
		elif wiz.report_type=='revenue_gerai':
			move_ids = self.pool.get('account.move.line').search(cr,uid,[],limit=1)
			datas.update({'ids':move_ids})
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'revenue.package',
					'datas': datas
					}
		elif wiz.report_type=='revenue_perwakilan':
			move_ids = self.pool.get('account.move.line').search(cr,uid,[],limit=1)
			datas.update({'ids':move_ids})
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'revenue.package',
					'datas': datas
					}
