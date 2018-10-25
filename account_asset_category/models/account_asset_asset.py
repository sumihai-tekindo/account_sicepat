from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_invoice_line(osv.osv):

	_inherit = 'account.invoice.line'
	
	def asset_create(self, cr, uid, lines, context=None):

		return True


