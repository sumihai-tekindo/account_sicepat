from openerp import models, fields, api

class account_invoice(models.Model):
	_inherit = 'account.invoice'


	aset_rental_id = fields.Many2one("asset.rental","Asset Rental")

class asset_rental(models.Model):
	_inherit ='asset.rental'

	mobile= fields.Char("Mobile Phone")
	phone = fields.Char("Phone")
	street = fields.Text("Address")
	insurer_id = fields.Many2one('res.partner','Supplier')

	@api.onchange('insurer_id')  # if these fields are changed, call  method
	def check_change(self):
		if self.insurer_id:
			self.mobile = self.insurer_id.mobile


	@api.onchange('insurer_id')  # if these fields are changed, call  method
	def check_change1(self):
		if self.insurer_id:
			self.phone = self.insurer_id.phone

	@api.onchange('insurer_id')  # if these fields are changed, call  method
	def check_change2(self):
		if self.insurer_id:
			self.street = self.insurer_id.street