from openerp.osv import osv,fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools.safe_eval import safe_eval as eval

class account_payment_term(osv.osv):
	_inherit = "account.payment.term"

	def compute(self, cr, uid, id, value, date_ref=False, context=None):
		if not context:context={}
		result = super(account_payment_term,self).compute(cr,uid,id,value,date_ref=date_ref,context=context)
		if not date_ref:
			date_ref = datetime.now().strftime('%Y-%m-%d')
		pt = self.browse(cr, uid, id, context=context)
		amount = value
		#override result
		result = []
		obj_precision = self.pool.get('decimal.precision')
		prec = obj_precision.precision_get(cr, uid, 'Account')
		override_date = False
		for line in pt.line_ids:
			if line.value == 'fixed':
				amt = round(line.value_amount, prec)
			elif line.value == 'procent':
				amt = round(value * line.value_amount, prec)
			elif line.value == 'balance':
				amt = round(amount, prec)
			if amt:
				next_date = override_date or (datetime.strptime(date_ref, '%Y-%m-%d') + relativedelta(days=line.days))
				if line.days2 < 0:
					next_first_date = next_date + relativedelta(day=1,months=1) #Getting 1st of next month
					next_date = next_first_date + relativedelta(days=line.days2)
				if line.days2 > 0:
					next_date += relativedelta(day=line.days2, months=1)
				if line.days3 >0:
					if line.days3>31 or line.days3<0:
						raise osv.except_osv(_('Error!'),_("Date of month should be on range 0-31"))
					if line.days3 in range(0,32) and (line.days2!=0 or line.days!=0):
						raise osv.except_osv(_('Error!'),_("Number of Days and Day of the Month should be 0"))
					elif line.days3 in range(0,32) and (line.days2==0 or line.days==0):
						next_date = override_date or (datetime.strptime(date_ref, '%Y-%m-%d').replace(day=line.days3) + relativedelta(days=line.days))
						next_date += relativedelta(months=1)
						override_date = next_date
						result.append( (next_date.strftime('%Y-%m-%d'), amt) )
						amount -= amt
						continue
				result.append( (next_date.strftime('%Y-%m-%d'), amt) )
				amount -= amt

		amount = reduce(lambda x,y: x+y[1], result, 0.0)
		dist = round(value-amount, prec)
		if dist:
			result.append( (time.strftime('%Y-%m-%d'), dist) )

		return result


class account_payment_term_line(osv.osv):
	_inherit = "account.payment.term.line"
	_columns = {
		"days3":fields.integer("Date of month",help="If > 0 and <=31, it will generate due date based on the date, if it is larger than last date of month, it will be automatically corrected as last date of month")
		}

	_order = "id asc,value desc,days"