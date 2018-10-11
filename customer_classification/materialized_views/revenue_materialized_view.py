from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.osv import fields,osv

class cust_grade_statistics(osv.osv):
	_name = "cust.grade.statistics"
	_description = "Customer Revenue Statistics"
	_auto = False
	
	_inherit = [
        'abstract.materialized.sql.view',
    ]
	_columns = {
		"id"						: fields.integer("ID"),
		"name"						: fields.char("Rev. Name"),
		"partner_id"				: fields.many2one("res.partner","Customer",required=True),
		"period_id"					: fields.many2one("account.period","Period"),
		"period_start"				: fields.date("Start Period"),
		"period_end"				: fields.date("End Period"),
		"curr_net_rev"				: fields.float("Curr. Net. Revenue"),
		"curr_rev_bef_revision"		: fields.float("Curr. Revenue Before Revision"),
		"curr_revision"				: fields.float("Curr. Revision"),
		"sales_id" 					: fields.many2one("res.users","Sales Person"),
		# "curr_gross_rev"	: fields.float("Curr. Gross. Revenue"),
		# "curr_paid_rev"		: fields.float("Curr. Paid Revenue"),
		# "curr_unpaid_rev"	: fields.float("Curr. Unpaid Revenue"),
	}

	
	# _sql_view_definition = """SELECT ROW_NUMBER() OVER(ORDER BY aml.period_id ASC, aml.partner_id ASC) as id,
	# 			trim(rp.name)||' - '||ap.code as name,
	# 			aml.partner_id, 
	# 			aml.period_id as period_id,
	# 			ap.date_start as period_start,
	# 			ap.date_stop as period_end,
	# 			rp.user_id as sales_id,
	# 			sum(aml.credit-aml.debit) as curr_net_rev,
	# 			sum(aml.credit) as curr_rev_bef_revision,
	# 			sum(aml.debit) as curr_revision
	# 		FROM account_move_line aml
	# 		INNER JOIN account_move am ON aml.move_id=am.id AND am.state='posted'
	# 		INNER JOIN account_account aa ON aml.account_id=aa.id
	# 		INNER JOIN account_journal aj ON aml.journal_id=aj.id 
	# 		INNER JOIN account_account_type aat ON aa.user_type=aat.id
	# 		INNER JOIN account_period ap ON aml.period_id=ap.id
	# 		INNER JOIN res_partner rp ON aml.partner_id=rp.id
	# 		LEFT JOIN res_users ru ON rp.user_id=ru.id
	# 		WHERE 
	# 			aml.date>=(date_trunc('month', CURRENT_DATE) - interval '12 month')::DATE 
	# 			AND aml.date<=(date_trunc('month', CURRENT_DATE) + interval '1 month - 1 day')::DATE
	# 			AND aj.type in ('sale','sale_refund') 
	# 			AND aj.compute_as_cb is True 
	# 			AND aat.report_type='income'
	# 		GROUP BY aml.partner_id, aml.period_id ,rp.name, rp.user_id, ap.code, ap.date_start, ap.date_stop"""

	_sql_view_definition = """select ROW_NUMBER() OVER(ORDER BY dummy.period_id ASC, dummy.partner_id ASC) as id, 
				dummy.name,
				dummy.partner_id,
				dummy.period_id,
				dummy.period_start,
				dummy.period_end,
				dummy.sales_id,
				sum(dummy.credit-dummy.debit) as curr_net_rev,
				sum(dummy.credit) as curr_rev_bef_revision,
				sum(dummy.debit) as curr_revision from (
					SELECT 
						trim(rp.name)||' - '||coalesce(apr.code,ap.code) as name,
						aml.partner_id, 
						coalesce(aml.revenue_revision_period_id,aml.period_id) as period_id,
						coalesce(apr.date_start,ap.date_start) as period_start,
						coalesce(apr.date_stop,ap.date_stop) as period_end,
						rp.user_id as sales_id,
						aml.debit,
						aml.credit
					FROM account_move_line aml
					INNER JOIN account_move am ON aml.move_id=am.id AND am.state='posted'
					INNER JOIN account_account aa ON aml.account_id=aa.id
					INNER JOIN account_journal aj ON aml.journal_id=aj.id 
					INNER JOIN account_account_type aat ON aa.user_type=aat.id
					LEFT JOIN account_period apr ON aml.revenue_revision_period_id=apr.id
					INNER JOIN account_period ap ON aml.period_id=ap.id
					INNER JOIN res_partner rp ON aml.partner_id=rp.id
					LEFT JOIN res_users ru ON rp.user_id=ru.id
					WHERE 
						aml.date>=(date_trunc('month', CURRENT_DATE) - interval '12 month')::DATE 
						AND aml.date<=(date_trunc('month', CURRENT_DATE) + interval '1 month - 1 day')::DATE
						AND aj.type in ('sale','sale_refund') 
						AND aj.compute_as_cb is True 
						AND aat.report_type='income'
					) dummy
			GROUP BY partner_id,period_id ,name, sales_id, period_start, period_end"""


	def init(self, cr):
		super(cust_grade_statistics,self).init(cr)
		cr.execute("""CREATE UNIQUE INDEX IF NOT EXISTS partner_period ON cust_grade_statistics (partner_id, period_id);""")
		cr.execute("""CREATE INDEX IF NOT EXISTS period_start ON cust_grade_statistics (period_start);""")
		cr.execute("""CREATE INDEX IF NOT EXISTS period_end ON cust_grade_statistics (period_end);""")