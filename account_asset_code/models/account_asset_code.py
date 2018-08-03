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


class account_asset_asset_add(osv.osv):
	_inherit = "account.asset.asset"


	_columns = {
		'code_asset'	: fields.char("Asset Code", readonly=True),
		#'variant'		: fields.many2one('product.product','Variant', required=False, change_default=True)
	}

	def validate(self, cr, uid, ids, context=None):
		asset_ids = self.browse(cr, uid, ids)
		for asset_id in asset_ids :
			if asset_id.code_asset :
				continue
			sequence_id = asset_id.invoice_line_id.product_id.categ_id.sequence1
			if not sequence_id :
				raise osv.except_osv(_('Warning !'), _('Sub Category must be fill in Product Category.'))
			obj_sequence = self.pool.get('ir.sequence')
			final_sequence = obj_sequence.next_by_id(cr, uid, sequence_id.id, context=context)
			
			picking_id = asset_id.invoice_line_id.purchase_line_id.order_id.picking_ids[:1]
			
			if picking_id :
				date_done = picking_id.date_done
				if date_done :
					date = date_done[5:7]
					year = date_done[2:4]
					first_seq = final_sequence[:8]
					end_seq = final_sequence[9:]
					code_asset = asset_id.invoice_line_id.product_id.code_asset
					if not code_asset :
						raise osv.except_osv(_('Warning !'), _('Please fill Asset Code in Product Variant first.'))
					final_sequence = '%s%s/%s/%s/%s'%(first_seq, code_asset, date, year, end_seq)

			asset_id.write({'code_asset':final_sequence})
		return super(account_asset_asset_add, self).validate(cr, uid, ids, context)