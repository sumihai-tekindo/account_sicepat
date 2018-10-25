from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning
from openerp import models, fields, api


class account_advance_payment_inv(models.Model):
	_name = "account.advance.payment.inv"
	_description = "account Advance Payment Invoice"

	product_id = fields.Many2one('product.product', 'Product',
		domain=[('type', '=', 'service')],)
	amount= fields.Float('Amount', digits_compute= dp.get_precision('Account'),)


	@api.multi
	def create_invoice(self):
		active_id = self._context.get('active_id')
		invoice_id = self.env['account.invoice'].browse(active_id)
		vals = self.get_invoice_vals(invoice_id)
		new_invoice_id = self.env['account.invoice'].create(vals)
		invoice_id.invoice_dp = new_invoice_id.id

	@api.multi
	def get_invoice_vals(self,invoice_id):
		active_id = self._context.get('active_id')
		invoice_id = self.env['account.invoice'].browse(active_id)
		invoice_line_vals = []
		for line in invoice_id.invoice_line :
			invoice_line_vals.append((0,False,{'name':line.name,'product_id':line.product_id.id,'price_unit':-1 * line.price_unit,'quantity':line.quantity,'account_id':line.account_id.id}))
			
		invoice_line_vals.append((0,False,{'name':self.product_id.name,'product_id':self.product_id.id,'price_unit':self.amount,'quantity':line.quantity,'account_id':self.product_id.property_account_expense.id}))
	
		invoice_vals = {'partner_id':invoice_id.partner_id.id,
		'company_id':invoice_id.company_id.id,
		'department_id':invoice_id.department_id.id,
		'user_id':invoice_id.user_id.id,
		'journal_id':invoice_id.journal_id.id,
		'account_id':invoice_id.account_id.id,
		'date_due':invoice_id.date_due,
		'currency_id':invoice_id.currency_id.id,
		'partner_bank_id':invoice_id.partner_bank_id.id,
		'date_invoice':invoice_id.date_invoice,
		'origin': invoice_id.internal_number,
		'invoice_line':invoice_line_vals,
		'comment':'REFUND KE SICEPAT EXPRESS' if invoice_id.amount_total > self.amount else ' '

		}
		
		return invoice_vals
		
		
	@api.multi	
	def _create_invoices(self, cr, uid, inv_values, purchase_id, context=None):
		inv_obj = self.pool.get('account.invoice')
		# purchase_obj = self.pool.get('purchase.order')
		journal_obj = self.pool['account.invoice'].default_get(cr, uid, ['journal_id'], context=context)['journal_id']
		inv_id = inv_obj.create(cr, uid, inv_values, context=context)
		inv_obj.button_reset_taxes(cr, uid, [inv_id], context=context)
		# purchase_obj.write(cr, uid, purchase_id, {'invoice_ids': [(4, inv_id)],'is_downpayment':True}, context=context)
		return inv_id
		

	

class account_invoice(models.Model):
	_inherit = "account.invoice" 

	invoice_dp=fields.Many2one('account.invoice','Invoice DP')
	is_downpayment=fields.Boolean('Advance Payment')

	@api.multi
	def open_invoices(self,inv_ids):
		if  self.invoice_dp.id:
			domain = [('id','=',self.invoice_dp.id)]
			# print"==========+++++++++++++===================",domain
			inv_ids = self.env['account.invoice'].search([('id','=',self.id)])
			context_domain = [('id','in',inv_ids)]
			# print"==========+++++++++++2++===================",context_domain
			invoice_ids = self.env['account.invoice'].search([('id','=',self.invoice_dp.id)])
			old_id = self.id
			new_id = invoice_ids.id
			
		
			return {
				'type': 'ir.actions.act_window',
				'name': 'Supplier Invoice',
				'res_model': 'account.invoice',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_id': new_id,
				'target': 'current',
				'domain': domain,
				# 'nodestroy': True,
				'flags': {'form': {'action_buttons': True}}
				}
		else:	
			raise Warning('Dont have any Payment who related this Invoice')	

