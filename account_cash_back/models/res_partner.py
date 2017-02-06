from openerp.osv import fields,osv
from datetime import datetime
from dateutil.relativedelta import relativedelta

class res_partner(osv.osv):
	_inherit = "res.partner"

	def _get_current_discounts(self, cr, uid, ids, field_names, args, context=None):
		res = {}
		if not context:context={}
		for partner in self.browse(cr,uid,ids,context=context):
			res.update({partner.id:0.0})
			if partner.discount_history_ids:
				res.update({partner.id:partner.discount_history_ids[0] and partner.discount_history_ids[0].name or 0.0})
		return res

	def _get_discount_histories(self, cr, uid, ids, context=None):
		#this function search for the partners linked to all account.move.line 'ids' that have been changed
		partners = set()
		for disc in self.browse(cr, uid, ids, context=context):
			if disc.partner_id:
				partners.add(disc.partner_id.id)
		return list(partners)

	_columns = {
		"current_discount": fields.function(_get_current_discounts, string='Discount', method=True, type='float',
			 store={
					'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['discount_history_ids'], 10),
					'res.partner.discounts': (_get_discount_histories,  ['name','sequence','start_date','end_date'], 10)
				   }),
		"discount_history_ids": fields.one2many("res.partner.discounts","partner_id","Discount Histories"),
	}

	_defaults ={
	'current_discount': 0.0,
	}

class res_partner_discounts(osv.osv):
	_name = "res.partner.discounts"

	_columns = {
		"name" 		: fields.float("Discount",help="Discount in percentage",required=True),
		"sequence"	: fields.integer("Sequence",required=True),
		"start_date": fields.date("Start Date",required=True),
		"end_date"	: fields.date("End Date",required=True),
		"partner_id": fields.many2one("res.partner","Customer",required=True,),
	}
	
	_order = "start_date desc,end_date desc,sequence desc"

	def _get_default_sequence(self,cr,uid,context=None):
		if not context:
			context={}
		current = 0
		partner_id = context.get('partner_id',False)
		if partner_id:
			query_pool = """select coalesce(max(sequence),0)::int  from res_partner_discounts where partner_id=%s"""%(partner_id)
			cr.execute(query_pool)
			current = cr.fetchone()
		return current and current[0]+1

	def _get_start_date(self,cr,uid,context=None):
		if not context:context={}
		start_date = datetime.now().strftime('%Y-%m-%d')

		return start_date

	def _get_end_date(self,cr,uid,context=None):
		if not context:context={}
		end_date = (datetime.now() + relativedelta(months=1)).strftime('%Y-%m-%d')
		return end_date
	def _get_partner(self,cr,uid,context=None):
		if not context:context={}
		if context.get('partner_id',False):
			return partner_id
		return False
	_defaults = {
		"name":0.0,
		"sequence"	: _get_default_sequence,
		"partner_id": _get_partner,
		"start_date": _get_start_date,
		"end_date"	: _get_end_date
	}