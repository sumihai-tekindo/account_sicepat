from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class purchase_order(osv.osv):
	_inherit = "purchase.order"
	
	_columns = {
	'invoice_method' : fields.selection([
		('manual','Based on Purchase Order lines'),
		('order','Based on generated draft invoice'),
		('picking','Based on incoming shipments'),
		('downpayment','Advance Payment (DP)')],
		 'Invoicing Control', required=True,
			readonly=True, states={'draft':[('readonly',False)],
			 'sent':[('readonly',False)]},),

	'is_downpayment':fields.boolean('Advance Payment',default=False,readonly=False),
	'invoice_dp_ids':fields.many2many('account.invoice','purchase_order_invoice_dp_rel','invoice_id','purchase_id','Invoice DP'),}
	
	def onchange_method(self,cr,uid,ids,invoice_method,is_downpayment,context=None):
		value = {'is_downpayment':False}
		if invoice_method =='downpayment':
			inv_method = self.pool.get('purchase.order').browse(cr,uid,invoice_method)
			value.update({'is_downpayment':True})
