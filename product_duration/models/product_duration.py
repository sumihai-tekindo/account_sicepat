from openerp import models, fields, api


class duration(models.Model):
	_inherit = "res.company"

	duration = fields.Integer(string='Duration')

