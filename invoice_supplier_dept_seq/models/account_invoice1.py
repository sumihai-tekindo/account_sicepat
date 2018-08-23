from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.osv import fields as f

class account_invoice(models.Model):
	_inherit = "account.invoice"

	department_id = fields.Many2one('account.invoice.department', 'Department', readonly=True, states={'draft': [('readonly', False)]}, copy=False, ondelete='set null')

	@api.cr_uid_context
	def create(self, cr, uid, vals,context=None):
		if not context:context={}
		obj_sequence = self.pool.get('ir.sequence')
		obj_journal = self.pool.get('account.journal')
		obj_dept = self.pool.get('account.invoice.department')
		number = ''
		journal = self._default_journal(cr,uid,context=context)
		# context=self._context.copy()

		date_invoice = vals.get('date_invoice', f.date.context_today(self,cr,uid,context=context))
		
		if vals.get('journal_id') and vals['journal_id']:
			journal = obj_journal.browse(cr,uid,vals['journal_id'])

		if vals.get('department_id') and vals['department_id']:
			department = obj_dept.browse(cr,uid,vals['department_id'])
		
		if context.get('type', False) in ('in_invoice', 'in_refund') or (vals.get('type') and vals['type'] in ('in_invoice', 'in_refund')):
			if journal.sequence_id:
				ctx = dict(context)
				ctx['ir_sequence_date'] = date_invoice
				number = obj_sequence.next_by_id(cr,uid,journal.sequence_id.id)
			else:
				raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))
			if number:
				number = "%s/%s" % (department.name, number)
				vals['internal_number'] = number
		
		res_id = super(account_invoice, self).create(cr,uid,vals,context)
		if context.get('type', False) in ('in_invoice', 'in_refund') or (vals.get('type') and vals['type'] in ('in_invoice', 'in_refund')):
			self.pool.get('account.invoice').write(cr,uid,[res_id], {'number': number})
		return res_id

	@api.multi
	def action_cancel(self):
		res = super(account_invoice, self).action_cancel()
		if self.type in ('in_invoice', 'in_refund'):
			self.write({'number': self.internal_number})
		return res

	@api.multi
	def finalize_invoice_move_lines(self, move_lines):
		""" finalize_invoice_move_lines(move_lines) -> move_lines

			Hook method to be overridden in additional modules to verify and
			possibly alter the move lines to be created by an invoice, for
			special cases.
			:param move_lines: list of dictionaries with the account.move.lines (as for create())
			:return: the (possibly updated) final move_lines to create for this invoice
		"""
		for move in move_lines:
			move[2]['department_id'] = self.department_id and self.department_id.id or False
		self.with_context(self._context,department_id = self.department_id and self.department_id.id or False)
		return move_lines



class account_journal(models.Model):
	_inherit = "account.journal"


	department_id = fields.Many2one('account.invoice.department','Department')

class account_move(models.Model):
	_inherit="account.move"

	
	# def _get_default_dept_id(self,):
	# 	dept_id = False
	# 	if self._context and self._context.get('department_id',False):
	# 		dept_id = self._context.get('department_id',False)
	# 	return dept_id

	@api.onchange('journal_id')
	def onchange_journal_id(self,):
		context=self._context.copy()
		self.department_id = self.journal_id.department_id and self.journal_id.department_id.id or False
		

	journal_id = fields.Many2one('account.journal','Journal')
	department_id = fields.Many2one('account.invoice.department','Department')




class account_move_line(models.Model):
	_inherit="account.move.line"

	def _get_default_dept_id(self,):
		dept_id = False
		if self._context and self._context.get('department_id',False):
			dept_id = self._context.get('department_id',False)
		return dept_id

	department_id = fields.Many2one('account.invoice.department','Department',default=_get_default_dept_id)
