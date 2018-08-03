from openerp import models, fields, api


class productcategory(models.Model):
	_inherit = "product.category"

	code = fields.Char("Asset Code",readonly=False)
	sequence1=fields.Many2one('ir.sequence','Sequence',required=False,domain=[('code', '=', 'account.asset.asset')])
