import itertools
import math
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_invoice(models.Model):
	_inherit = "account.invoice"

	
	revenue_revision_period_id = fields.Many2one("account.period","Revenue Revision Period")
	

	@api.multi
	def finalize_invoice_move_lines(self, move_lines):
		""" finalize_invoice_move_lines(move_lines) -> move_lines

			Hook method to be overridden in additional modules to verify and
			possibly alter the move lines to be created by an invoice, for
			special cases.
			:param move_lines: list of dictionaries with the account.move.lines (as for create())
			:return: the (possibly updated) final move_lines to create for this invoice
		"""
		move_lines = super(account_invoice,self).finalize_invoice_move_lines(move_lines)

		if self.type=='out_refund' and self.revenue_revision_period_id and self.revenue_revision_period_id.id:
			for mvl in move_lines:
				mvl[2]['revenue_revision_period_id']=self.revenue_revision_period_id.id
		return move_lines