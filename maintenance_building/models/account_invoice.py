from openerp import models, fields, api

class account_invoice(models.Model):
	_inherit = 'account.invoice'


	aset_rental_id = fields.Many2one("asset.rental","Asset Rental")

class asset_rental(models.Model):
	_inherit ='asset.rental'

	@api.one
	@api.depends('insurer_id')
	def _compute_field1(self):
		self.mobile = self.insurer_id.mobile
		self.phone = self.insurer_id.phone
		self.street = self.insurer_id.street

	@api.one
	@api.depends('insurer_id')  # if these fields are changed, call  method
	def _check_change(self):
		self.phone = self.insurer_id.phone

	@api.one
	@api.depends('insurer_id')  # if these fields are changed, call  method
	def _check_change(self):
		self.street = self.insurer_id.street	

	@api.one
	@api.depends('branch')  # if these fields are changed, call  method
	def _check_changebranch(self):
		self.alamat_lengkap = self.branch.alamat_lengkap

	# mobile=fields.Char(compute=_compute_field1,store=True)
	# phone = fields.Char(compute=_compute_field1,store=True)
	# street = fields.Text(compute=_check_change,store=True)
	# insurer_id = fields.Many2one('res.partner','Supplier')
	# alamat_lengkap = fields.Text(compute=_check_changebranch,store=True)
	# branch = fields.Many2one('account.analytic.account','Branch')

	mobile=fields.Char(compute=_compute_field1,store=True)
	phone = fields.Char(compute=_compute_field1,store=True)
	street = fields.Text(compute=_check_change,store=True)
	insurer_id = fields.Many2one('res.partner','Supplier')
	alamat_lengkap = fields.Text(compute=_check_changebranch,store=True)
	branch = fields.Many2one('account.analytic.account','Branch')