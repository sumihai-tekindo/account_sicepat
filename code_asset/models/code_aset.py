from openerp import models, fields, api


class productasset(models.Model):
	_inherit = "product.template"
	code_asset = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D'),('E', 'E'),('F', 'F'),('G', 'G'),('H', 'H'),('I', 'I'),('J', 'J'),('K', 'K'),('L', 'L'),('M', 'M'),('N', 'N'),('O', 'O'),('P', 'P'),('Q', 'Q'),('R', 'R'),('S', 'S'),('T', 'T'),('U', 'U'),('V', 'V'),('W', 'W'),('X', 'X'),('Y', 'Y'),('Z', 'Z')])
	#code_asset = fields.Char("Asset Code",readonly=False, size=3)

class productproduct(models.Model):
	_inherit = "product.product"
	
	#code_asset = fields.Selection("Asset Code",readonly=False)
	code_asset = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D'),('E', 'E'),('F', 'F'),('G', 'G'),('H', 'H'),('I', 'I'),('J', 'J'),('K', 'K'),('L', 'L'),('M', 'M'),('N', 'N'),('O', 'O'),('P', 'P'),('Q', 'Q'),('R', 'R'),('S', 'S'),('T', 'T'),('U', 'U'),('V', 'V'),('W', 'W'),('X', 'X'),('Y', 'Y'),('Z', 'Z')])

# class productcateg(models.Model):
# 	_inherit = "product.category"

# 	code = fields.Char("Asset Code",readonly=False, size=3)


