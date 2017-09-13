# 1 : imports of python lib
import logging

# 2 :  imports of openerp
from openerp import fields, models, api
from openerp.osv import osv
from openerp.tools.misc import pickle
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class res_company_inherit(models.Model):
	_inherit = "res.company"

	receivable_ids = fields.Many2many('account.account','company_account_rel','account_id','company_id',string='Receivables')



