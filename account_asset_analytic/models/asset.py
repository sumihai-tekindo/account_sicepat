import time
import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp.tools import float_is_zero
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'
    
    def asset_create(self, cr, uid, lines, context=None):
        context = context or {}
        asset_obj = self.pool.get('account.asset.asset')
        asset_ids = []
        for line in lines:
            if line.invoice_id.number:
                #FORWARDPORT UP TO SAAS-6
                asset_ids += asset_obj.search(cr, SUPERUSER_ID, [('code', '=', line.invoice_id.number), ('company_id', '=', line.company_id.id)], context=context)
        asset_obj.write(cr, SUPERUSER_ID, asset_ids, {'active': False})
        for line in lines:
            if line.asset_category_id:
                #FORWARDPORT UP TO SAAS-6
                sign = -1 if line.invoice_id.type in ("in_refund", 'out_refund') else 1
                vals = {
                    'name': line.name,
                    'code': line.invoice_id.number or False,
                    'category_id': line.asset_category_id.id,
                    'purchase_value': sign * line.price_subtotal,
                    'partner_id': line.invoice_id.partner_id.id,
                    'company_id': line.invoice_id.company_id.id,
                    'currency_id': line.invoice_id.currency_id.id,
                    'purchase_date' : line.invoice_id.date_invoice,
                    'invoice_line_id': line.id or False,
                    'invoice_id': line.invoice_id.id or False,
                }
                changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'], context=context)
                vals.update(changed_vals['value'])
                asset_id = asset_obj.create(cr, uid, vals, context=context)
                if line.asset_category_id.open_asset:
                    asset_obj.validate(cr, uid, [asset_id], context=context)
        return True



class account_asset_asset(osv.osv):
	_inherit = "account.asset.asset"

	_columns = {
		"account_analytic_id"	: fields.many2one("account.analytic.account","Analytic Account"),
		"invoice_line_id"		: fields.many2one("account.invoice.line","Invoice Line"),
		"invoice_id"			: fields.many2one("account.invoice","Invoice"),
		"move_in_id"			: fields.many2one("stock.move","Incoming Source"),
		"move_out_id"			: fields.many2one("stock.move","Transfer Source"),
	}


	def compute_stock_move(self,cr,uid,ids,context=None):
		if not context:context={}
		existing_move_out = self.search(cr,uid,[])
		existing_move_out_ids = [ass.move_out_id.id for ass in self.browse(cr,uid,existing_move_out) if ass.move_out_id and ass.move_out_id.id]
		for asset in self.browse(cr,uid,ids,context=context):
			move_in_id  = asset.move_in_id and asset.move_in_id.id or False
			move_out_id = asset.move_out_id and asset.move_out_id.id or False
			account_analytic_id = asset.account_analytic_id and asset.account_analytic_id.id or False
			if (asset.code and asset.code!='') or (asset.invoice_id and asset.invoice_line_id):
				if asset.invoice_line_id and asset.invoice_line_id.id:
					incomings = [asset.invoice_line_id.move_line_ids]
					move_in_id  = incomings and incomings[0].id
					quant_ids = incomings and [q.id for q in incomings[0].quant_ids if q.location_id.usage=='production']
					move_out_ids = self.pool.get('stock.move').search(cr,uid,[('quant_ids','in',quant_ids),('location_dest_id.usage','=','production'),('id','not in',existing_move_out_ids)])
					if move_out_ids and move_out_ids[0]:
						move_out_id = move_out_ids[0]
						mv_out = self.pool.get('stock.move').browse(cr,uid,move_out_id)
						account_analytic_id = mv_out.account_analytic_dest_id and mv_out.account_analytic_dest_id.id 
					else:
						account_analytic_id = incomings and incomings[0].location_dest_id and incomings[0].location_dest_id.account_analytic_id and incomings[0].location_dest_id.account_analytic_id.id or False
						# print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",incomings,account_analytic_id
			asset.write({'move_in_id':move_in_id,'move_out_id':move_out_id,'account_analytic_id':account_analytic_id})

		return True		


class account_asset_depreciation_line(osv.osv):
	_inherit = 'account.asset.depreciation.line'

	def create_move(self, cr, uid, ids, context=None):
		context = dict(context or {})
		can_close = False
		asset_obj = self.pool.get('account.asset.asset')
		period_obj = self.pool.get('account.period')
		move_obj = self.pool.get('account.move')
		move_line_obj = self.pool.get('account.move.line')
		currency_obj = self.pool.get('res.currency')
		created_move_ids = []
		asset_ids = []
		for line in self.browse(cr, uid, ids, context=context):
			depreciation_date = context.get('depreciation_date') or line.depreciation_date or time.strftime('%Y-%m-%d')
			period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
			company_currency = line.asset_id.company_id.currency_id.id
			current_currency = line.asset_id.currency_id.id
			context.update({'date': depreciation_date})
			amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
			sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
			asset_name = "/"
			reference = line.asset_id.name
			move_vals = {
				'name': asset_name,
				'date': depreciation_date,
				'ref': reference,
				'period_id': period_ids and period_ids[0] or False,
				'journal_id': line.asset_id.category_id.journal_id.id,
				}
			move_id = move_obj.create(cr, uid, move_vals, context=context)
			journal_id = line.asset_id.category_id.journal_id.id
			partner_id = line.asset_id.partner_id.id
			prec = self.pool['decimal.precision'].precision_get(cr, uid, 'Account')
			move_line_obj.create(cr, uid, {
				'name': asset_name,
				'ref': reference,
				'move_id': move_id,
				'account_id': line.asset_id.category_id.account_depreciation_id.id,
				'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
				'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
				'period_id': period_ids and period_ids[0] or False,
				'journal_id': journal_id,
				'partner_id': partner_id,
				'currency_id': company_currency != current_currency and  current_currency or False,
				'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
				'date': depreciation_date,

			})

			analytic_id = line.asset_id and line.asset_id.account_analytic_id and line.asset_id.account_analytic_id.id or line.asset_id.category_id.account_analytic_id.id or False

			move_line_obj.create(cr, uid, {
				'name': asset_name,
				'ref': reference,
				'move_id': move_id,
				'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
				'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
				'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
				'period_id': period_ids and period_ids[0] or False,
				'journal_id': journal_id,
				'partner_id': partner_id,
				'currency_id': company_currency != current_currency and  current_currency or False,
				'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
				'analytic_account_id': analytic_id,
				'date': depreciation_date,
				'asset_id': line.asset_id.id,
			})
			self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
			created_move_ids.append(move_id)
			asset_ids.append(line.asset_id.id)
		# we re-evaluate the assets to determine whether we can close them
		for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
			if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
				asset.write({'state': 'close'})
		return created_move_ids