from openerp.osv import fields,osv

class account_extra_report_wizard(osv.osv_memory):
	_name = "account.extra.report.wizard"

	_columns = {
	"report_type"	: fields.selection(
		[
		('daily_receivable','Laporan Piutang Harian'),
		('daily_payment','Laporan Penerimaan Uang dari Pelunasan Piutang'),
		('daily_cashflow','Laporan Cash Flow Harian'),
		('monthly_cashflow','Laporan Cash Flow Bulanan'),
		('outstanding_followup','Laporan Outstanding Piutang per Followup'),
		],"Jenis Laporan",required=True),
	"start_date"	: fields.date("Start Date" ,required=True),
	"end_date"		: fields.date("End Date" ,required=True),
	"display_detail": fields.boolean('Display Detail'),
	"display_payment": fields.boolean('Display Payment'),
	"group_by"		: fields.selection([('group_fiscal','By Fiscal'), ('group_partner','By Partner')],"Group by"),
	"account_ids"	: fields.many2many('account.account', 'account_account_extra_report_rel','wiz_id', 'account_id', 'Accounts'),
	}

	_defaults = {
		"report_type":'daily_receivable',
		"group_by":'group_fiscal',
	}

	def get_daily_receivable(self,cr,uid,ids,wiz,context=None):
		if not context:context={}
		if not wiz.account_ids:
			account_ids = self.pool.get('account.account').search(cr,uid,[('type','=','receivable'),('reconcile','=',True)])
		else:
			account_ids = [x.id for x in wiz.account_ids]
		credit_note_journal = self.pool.get('account.journal').search(cr,uid,[('type','=','sale_refund')])
		move_ids=[]
		move_ids_cn=[]
		if not wiz.start_date and not wiz.end_date:
			move_ids = self.pool.get('account.move.line').search(cr,uid,[('account_id','in',account_ids),('reconcile_id','=',False),('debit','>',0.0)])
			move_ids_cn = self.pool.get('account.move.line').search(cr,uid,[('account_id','in',account_ids),('reconcile_id','=',False),('credit','>',0.0),('journal_id','in',credit_note_journal)])
		else:
			dom = [('account_id','in',account_ids),('reconcile_id','=',False),('debit','>',0.0)]
			dom_cn = [('account_id','in',account_ids),('reconcile_id','=',False),('credit','>',0.0),('journal_id','in',credit_note_journal)]
			if wiz.start_date:
				dom.append(('date','>=',wiz.start_date))
			if wiz.end_date:
				dom.append(('date','<=',wiz.end_date))
			move_ids = self.pool.get('account.move.line').search(cr,uid,dom,context=context)
			move_ids_cn = self.pool.get('account.move.line').search(cr,uid,dom_cn,context=context)
		move_ids+=move_ids_cn
		return move_ids


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
			'display_detail': wiz.display_detail,
			'group_by': wiz.group_by,
			'display_payment': wiz.display_payment,
			}
		if wiz.report_type=='daily_receivable':
			#move_ids = self.get_daily_receivable(cr,uid,ids,wiz,context=context)
			move_ids = self.pool.get('account.move.line').search(cr,uid,[],limit=1)
			datas.update({'ids':move_ids})
			if wiz.display_detail:
				return {
						'type': 'ir.actions.report.xml',
						# 'report_name': 'daily.receivable.detail.xls',
						'report_name': 'daily.receivable.payment.detail',
						'datas': datas
						}
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'daily.receivable.report.xls',
					'datas': datas
					}
		elif wiz.report_type=='daily_payment':
			move_ids = self.pool.get('account.move.line').search(cr,uid,[],limit=1)
			datas.update({'ids':move_ids})
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'daily.payment.report.xls',
					'datas': datas
					}
		elif wiz.report_type=='daily_cashflow':
			move_ids = self.pool.get('account.move.line').search(cr,uid,[],limit=1)
			datas.update({'ids':move_ids})
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'daily.cashflow.report.xls',
					'datas': datas
					}
		elif wiz.report_type=='monthly_cashflow':
			move_ids = self.pool.get('account.move.line').search(cr,uid,[],limit=1)
			datas.update({'ids':move_ids})
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'monthly.cashflow.report.xls',
					'datas': datas
					}
		else:
			move_ids = self.pool.get('account.move.line').search(cr,uid,[],limit=1)
			datas.update({'ids':move_ids})
			if wiz.display_detail:
				return {
						'type': 'ir.actions.report.xml',
						'report_name': 'outstanding.followup.detail.xls',
						'datas': datas
						}
			return {
					'type': 'ir.actions.report.xml',
					'report_name': 'outstanding.followup.report.xls',
					'datas': datas
					}

