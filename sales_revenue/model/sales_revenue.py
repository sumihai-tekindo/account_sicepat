from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from openerp.addons.base.ir.ir_cron import _intervalTypes



class sales_revenue_rpt(models.Model):

    _name='sales.revenue.rpt'

    invoice_date = fields.Date('Invoice Date')
    gerai = fields.Many2one('account.analytic.account','Gerai')
    user_id = fields.Many2one('res.users','Sales')
    partner_id= fields.Many2one('res.partner','Customer')
    join_date = fields.Date('Join Date')
    will_be_count = fields.Integer('Will be Count')
    quantity = fields.Float('Quantiy', digits=(20,2))
    gross_amount = fields.Float('Gross Amount', digits=(20,2))
    weight=fields.Float('Weight', digits=(20,2))
    discount=fields.Float('Disc%', digits=(20,2))
    discount_amount=fields.Float('Discount',digits=(20,2))
    refund = fields.Float('Refund')
    net_revenue=fields.Float('Total Amount')
    service_type = fields.Many2one('consignment.service.type')
    tag=fields.Char('tag')
    type=fields.Char('Type')
