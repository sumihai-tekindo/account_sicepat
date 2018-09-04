# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models, fields, api

class SalesRevenueReport(models.Model):

	_name='sales.revenue.report'
	_description = "Sales Revenue"
	_auto = False
	_rec_name = 'date_invoice'

	date_invoice = fields.Date('Invoice Date', readonly=True)
	partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
	commercial_partner_id = fields.Many2one('res.partner', 'Partner Company', help="Commercial Entity")
	date_join = fields.Date('Join Date', readonly=True)
	new_partner = fields.Boolean('New Customer', readonly=True)
	user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
	account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic', readonly=True)
	store_id = fields.Many2one('res.store', 'Store', readonly=True)
	service_id = fields.Many2one('consignment.service.type', readonly=True)
	net_amount = fields.Float('Net Amount', readonly=True)
	refund = fields.Float('Refund', readonly=True)
	discount_amount = fields.Float('Discount', readonly=True)
	gross_amount = fields.Float('Gross Amount', readonly=True)
	waybill_count = fields.Integer('Waybill', readonly=True)
	quantity = fields.Float('Weigh (kg) ', readonly=True)

	_order = 'date_invoice DESC'

	_depends = {
		'account.invoice': [
			'account_id', 'commercial_partner_id', 'company_id',
			'currency_id', 'date_due', 'date_invoice',
			'journal_id', 'partner_bank_id', 'partner_id',
			'residual', 'state', 'type', 'user_id',
		],
		'account.invoice.line': [
			'account_id', 'invoice_id', 'price_subtotal', 'product_id',
			'price_unit', 'discount', 'quantity', 'account_analytic_id',
		],
# 		'product.product': ['product_tmpl_id'],
# 		'product.template': ['categ_id'],
# 		'product.uom': ['category_id', 'factor', 'name', 'uom_type'],
# 		'res.currency.rate': ['currency_id', 'name'],
		'res.partner': ['date', 'country_id'],
		'account.journal': ['cb_journal'],
		'consignment.service.type': ['name'],
		'res.store': ['code'],
	}

	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
		result = super(SalesRevenueReport, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
		return result

	def _select(self):
		select_str = """
			SELECT
				min(ail.id) AS id,
				ai.date_invoice,
				ai.partner_id,
				ai.commercial_partner_id,
				partner.date AS date_join, 
				CASE 
					WHEN ai.date_invoice = partner.date THEN true
					ELSE false
				END AS new_partner,
				ai.user_id,
				ail.account_analytic_id,
				store.id AS store_id,  
				CASE  
					WHEN service.id IS NULL THEN 1 
					WHEN service.id = 4 THEN 3
					ELSE service.id 
				END AS service_id, 
				CASE
					WHEN ai.type::text = ANY (ARRAY['out_invoice'::character varying::text]) THEN SUM(ail.price_subtotal + (ail.quantity * (ail.price_unit * (ail.discount/100))))
					ELSE 0.0
				END AS gross_amount,
				CASE 
					WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text]) THEN SUM(ail.price_subtotal) 
					ELSE 0.0
				END AS refund, 
				CASE 
					WHEN ai.type::text = ANY (ARRAY['out_invoice'::character varying::text]) THEN SUM(ail.quantity * (ail.price_unit * (ail.discount/100))) 
					ELSE 0.0 
				END AS discount_amount, 
				(invoice_type.sign*SUM(ail.price_subtotal)) AS net_amount, 
				(invoice_type.sign*COUNT(ail.id)) AS waybill_count, 
				(invoice_type.sign*SUM(ail.quantity)) AS quantity 
		"""
		return select_str

	def _from(self):
		from_str = """
			FROM 
				account_invoice_line ail 
				JOIN account_invoice ai ON ai.id = ail.invoice_id 
				JOIN res_partner partner ON ai.commercial_partner_id = partner.id 
				LEFT JOIN account_journal journal ON ai.journal_id = journal.id
				LEFT JOIN consignment_service_type service ON ail.layanan = service.id
				LEFT JOIN res_store store ON partner.name LIKE store.code || '%'
				JOIN (
					SELECT id,(CASE
						 WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_refund'::character varying::text])
							THEN -1
							ELSE 1
						END) AS sign
					FROM account_invoice ai
				) AS invoice_type ON invoice_type.id = ai.id
		"""
		return from_str

	def _where(self):
		where_str = """
			WHERE
				ai.type::text = ANY (ARRAY['out_invoice'::character varying::text, 'out_refund'::character varying::text])
				AND ai.state::text = ANY (ARRAY['open'::character varying::text, 'paid'::character varying::text])
				AND NOT journal.cb_journal
		"""
		return where_str

	def _group_by(self):
		group_by_str = """
			GROUP BY
				ai.date_invoice,
				ai.id,
				ai.partner_id,
				ai.commercial_partner_id,
				partner.date,
				ai.user_id,
				ail.account_analytic_id,
				service.id,
				store.id,
				invoice_type.sign
		"""
		return group_by_str

	def init(self, cr):
		tools.drop_view_if_exists(cr, self._table)
		cr.execute("""CREATE or REPLACE VIEW %(table)s as (
				%(select)s 
				%(from)s 
				%(where)s
				%(groupby)s
		)""" % {
				'table': self._table, 
				'select': self._select(), 
				'from': self._from(), 
				'where': self._where(), 
				'groupby': self._group_by(),
			})
