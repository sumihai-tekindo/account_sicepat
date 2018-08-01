from openerp import models, fields, api


class productcategory(models.Model):
	_inherit = "product.category"

	code = fields.Char("Asset Code",readonly=False)
	# sub_categ= fields.Many2one('product.category','Sub Category',required=False)
	# sub_categ_detail= fields.Many2one('product.category','Sub Category Detail',required=False)
	sequence= fields.Char("sequence",size=3)


# def onchange_case(self, cr, uid, ids, sequence):
#     result = {'value': {
#         'sequence': str(sequence).upper()
#         }
#     }
#     return result
	# @api.onchange('name')
	# def set_code(self):
	# 	self.code = self.product_category.name

	# @api.onchange('code')
	# def code(self):
	# 	if self.code:
	# 		self.code = self.product_category.name
	# @api.onchange('sub_categ')
	# def sub_categ(self):
	# 	if self.sub_categ:
	# 		self.parent_id = self.sub_categ.id

	# @api.onchange('sub_categ')
	# def sub_categ(self):
	# 	if self.sub_categ:
	# 		self.id = self.sub_detail_categ.id

	# @api.onchange('sub_categ_detail')
	# def sub_categ_detail(self):
	# 	if self.sub_categ_detail:
	# 		self.parent_id = self.product_category.sub_categ			

