from datetime import datetime
import time
import dateutil.parser
from openerp import fields, models, api
from openerp.tools.translate import _

class purchase_order(models.Model):
	_inherit = "purchase.order"

	contact_vendor_date = fields.Datetime('Contact Vendor')

	@api.one
	def compute_vendor(self,contact_vendor_date):
		today = fields.datetime.now()
	
		for purchase in self :
			purchase_id = purchase.id

		if purchase.contact_vendor_date == False:
			return self.write({'contact_vendor_date': today})

	


