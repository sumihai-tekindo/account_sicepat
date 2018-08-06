from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta

def str_to_datetime(strdate):
return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class purchase_order(osv.Model):
	_inherit = 'purchase.order'


def scheduler_manage_rent_expiration(self, cr, uid, context=None):
       
        datetime_today = datetime.datetime.strptime(fields.date.context_today(self, cr, uid, context=context), tools.DEFAULT_SERVER_DATE_FORMAT)
        limit_date = (datetime_today + relativedelta(days=+15)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        ids = self.search(cr, uid, ['&', ('date_end', '<', limit_date)], offset=0, limit=None, order=None, context=context, count=False)
        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            if purchase_order.purchase_order_id.id in res:
                res[purchase_order.purchase_order_id.id] += 1
            else:
                res[purchase_order.purchase_order_id.id] = 1

        for purchase_order_id, value in res.items():
            self.pool.get('purchase_order_id').message_post(cr, uid, purchase_order_id, body=_('%s contract(s) need(s) to be renewed and/or closed!') % (str(value)), context=context)
        return self.write(cr, uid, ids, {'state': 'toclose'}, context=context)
