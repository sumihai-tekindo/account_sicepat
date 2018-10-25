from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning

# class account_invoice(osv.osv):
# 	_inherit ="account.invoice"

# 	_columns ={'is_downpayment':fields.boolean('DP')

# 	}
class purchase_advance_payment_inv(osv.osv_memory):
	_name = "purchase.advance.payment.inv"
	_description = "purchase Advance Payment Invoice"


	_columns = {
		'advance_payment_method':fields.selection(
			[('fixed', 'Advance Payment (DP)'),('all', 'Full Payment')],
			'What do you want to invoice?', required=True,
			help="""Use Invoice the whole sale order to create the final invoice.
				Use Percentage to invoice a percentage of the total amount.
				Use Fixed Price to invoice a specific amound in advance.
				Use Some Order Lines to invoice a selection of the sales order lines."""),
		'qtty': fields.float('Quantity', digits=(16, 2), required=True),
		'product_id': fields.many2one('product.product', 'Advance Product',
			domain=[('type', '=', 'service')],
			help="""Select a product of type service which is called 'Advance Product'.
				You may have to create it and set it as a default value on this field."""),
		'amount': fields.float('Advance Amount', digits_compute= dp.get_precision('Account'),
			help="The amount to be invoiced in advance."),
		'amount_residual': fields.float('residual', digits_compute= dp.get_precision('Account')),

	} 
	
	def _onchange_residual(self, cr ,uid, ids, context=None):
		
		active_ids = context.get('active_ids')
		result = {'value':{}}
		if active_ids :
				purchase_ids = self.pool.get('purchase.order').browse(cr,uid, active_ids)
				for order in purchase_ids :
					total_dp = 0.0
					for dp in order.invoice_dp_ids :
						total_dp += dp.amount_total
					result['value']['amount_residual'] = order.amount_total - total_dp
		return result

	def _translate_advance(self, cr, uid, percentage=False, context=None):
		return _("Advance Payment of %s %%") if percentage else _("Advance Payment of %s %s")

	def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		purchase_obj = self.pool.get('purchase.order')
		ir_property_obj = self.pool.get('ir.property')
		fiscal_obj = self.pool.get('account.fiscal.position')
		inv_line_obj = self.pool.get('account.invoice.line')
		wizard = self.browse(cr, uid, ids[0], context)
		purchase_ids = context.get('active_ids', [])
		account_jrnl_obj = self.pool.get('account.journal')
		journal_id = account_jrnl_obj\
			.search(cr, uid, [('type', '=', 'purchase')], context=None)
		journal_id = journal_id and journal_id[0] or False
		result = []	
		for purchase in purchase_obj.browse(cr, uid, purchase_ids, context=context):
			val = inv_line_obj.product_id_change(cr, uid, [], wizard.product_id.id,
					False, partner_id=purchase.partner_id.id, fposition_id=purchase.fiscal_position.id,
					company_id=purchase.company_id.id)
			res = val['value']

			#determine and check income account
			if not wizard.product_id.id :
				prop = ir_property_obj.get(cr, uid,
							'property_account_income_categ', 'product.category', context=context)
				prop_id = prop and prop.id or False
				account_id = fiscal_obj.map_account(cr, uid, purchase.fiscal_position or False, prop_id)
				if not account_id:
					raise osv.except_osv(_('Configuration Error!'),
							_('There is no income account defined as global property.'))
				res['account_id'] = account_id
			if not res.get('account_id'):
				raise osv.except_osv(_('Configuration Error!'),
						_('There is no income account defined for this product: "%s" (id:%d).') % \
							(wizard.product_id.name, wizard.product_id.id,))
			# check condition 	
			
			if wizard.amount > wizard.amount_residual:
				raise Warning('Not allowed to Fill in the Amount more than Remaining Payment')
			if 	wizard.amount - wizard.amount_residual == 0.0 and wizard.advance_payment_method !='all':
				raise Warning('You must choose full Payment for Settlement') 

			# determine invoice amount
			if wizard.amount <= 0.00:
				raise osv.except_osv(_('Incorrect Data'),
					_('The value of Advance Amount must be positive.'))
			if wizard.advance_payment_method == 'percentage':
				inv_amount = purchase.amount_untaxed * wizard.amount / 100
				if not res.get('name'):
					res['name'] = self._translate_advance(cr, uid, percentage=True, context=dict(context, lang=purchase.partner_id.lang)) % (wizard.amount)
			else:
				inv_amount = wizard.amount
				if not res.get('name'):
					#TODO: should find a way to call formatLang() from rml_parse
					symbol = purchase.pricelist_id.currency_id.symbol
					if purchase.pricelist_id.currency_id.position == 'after':
						symbol_order = (inv_amount, symbol)
					else:
						symbol_order = (symbol, inv_amount)
					res['name'] = self._translate_advance(cr, uid, context=dict(context, lang=purchase.partner_id.lang)) % symbol_order

			# create the Line invoice
			inv_line_values = {
				'name': res.get('name'),
				'origin': purchase.name,
				'account_id': res['account_id'],
				'price_unit': inv_amount,
				'quantity': wizard.qtty or 1.0,
				'discount': False,
				'uos_id': res.get('uos_id', False),
				'product_id': wizard.product_id.id,
				'type':'in_invoice',
				# 'invoice_line_tax_id': res.get('invoice_line_tax_id'),
				# 'account_analytic_id': purchase.project_id.id or False,
			}
			inv_values = {
				'name': purchase.name,
				'origin': purchase.name,
				'type': 'in_invoice',
				'journal_id':journal_id,
				'reference': False,
				'account_id': purchase.partner_id.property_account_payable.id,
				'partner_id': purchase.partner_id.id,
				'invoice_line': [(0, 0, inv_line_values)],
				'currency_id': purchase.pricelist_id.currency_id.id,
				'comment': purchase.notes,
				'payment_term': purchase.payment_term_id,
				'fiscal_position': purchase.fiscal_position.id or purchase.partner_id.property_account_position.id,
				'department_id':purchase.department_id.id,
				'date_invoice':purchase.date_approve,
				# 'section_id': purchase.section_id.id,
			}
			result.append((purchase, inv_values))
		return result
   
	def _create_invoices(self, cr, uid, inv_values, purchase_id, context=None):
		inv_obj = self.pool.get('account.invoice')
		purchase_obj = self.pool.get('purchase.order')
		journal_obj = self.pool['account.invoice'].default_get(cr, uid, ['journal_id'], context=context)['journal_id']
		inv_id = inv_obj.create(cr, uid, inv_values, context=context)
		inv_obj.button_reset_taxes(cr, uid, [inv_id], context=context)
		purchase_obj.write(cr, uid, purchase_id, {'invoice_ids': [(4, inv_id)]}, context=context)
		return inv_id

	def create_invoices(self, cr, uid, ids, context=None):
		purchase_obj = self.pool.get('purchase.order')
		invoice_line_obj = self.pool.get('account.invoice.line')
		act_window = self.pool.get('ir.actions.act_window')
		inv_obj = self.pool.get('account.invoice')
		wizard = self.browse(cr, uid, ids[0], context)
		purchase_ids = context.get('active_ids', [])
		purchase_order_ids = purchase_obj.browse(cr,uid,purchase_ids)
		
		if wizard.advance_payment_method == 'all':
			invoice_ids = purchase_obj.action_invoice_create(cr, uid, purchase_ids, context)
			for purchase in purchase_obj.browse(cr,uid,purchase_ids):
				if purchase.invoice_dp_ids : 
					invoice_line_vals = {}
					for invoice_dp_id in purchase.invoice_dp_ids : 
						for invline in invoice_dp_id.invoice_line:
								invoice_line_vals[invline.id] = {
												'name': invline.name,
												'account_id': invline.account_id.id,
												'price_unit': -1 * invline.price_unit or 0.0,
												'quantity': invline.quantity,
												'product_id': invline.product_id.id or False,
												'uos_id': invline.uos_id.id or False,
												'invoice_id':invoice_ids,
												# 'account_analytic_id': invline.account_analytic_id.id or False,
												# 'purchase_line_id': order_line.id,
								 }

					for key ,value in invoice_line_vals.items() :
						invoice_line_id = invoice_line_obj.create(cr,uid,value,context=context)
					# purchase.write({'invoice_ids':[(4,invoice_ids)]})
					purchase.write({'invoice_ids':[(4,invoice_ids)]})
			if context.get('open_invoices', False):
				return  purchase_obj.invoice_open(cr,uid,purchase_ids,context)
			return {'type': 'ir.actions.act_window_close'}
		assert wizard.advance_payment_method in ('fixed','all')

		inv_ids = []
		for purchase_id, inv_values in self._prepare_advance_invoice_vals(cr, uid, ids, context=context):
			invoice_id = self._create_invoices(cr, uid, inv_values, purchase_id.id, context=context)
			inv_ids.append(invoice_id)
			purchase_id.write({'invoice_dp_ids':[(4,invoice_id)],'invoice_ids':[(4,invoice_id)],'is_downpayment':True},context=context)
			
		if context.get('open_invoices', False):
			return self.open_invoices( cr, uid, ids, inv_ids, context=context)
		return {'type': 'ir.actions.act_window_close'}

	def open_invoices(self, cr, uid, ids, invoice_ids, context=None):
		
		ir_model_data = self.pool.get('ir.model.data')
		form_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
		form_id = form_res and form_res[1] or False
		tree_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
		tree_id = tree_res and tree_res[1] or False

		return {
			'name': _('Advance Invoice'),
			'view_type': 'form',
			'view_mode': 'form,tree',
			'res_model': 'account.invoice',
			'res_id': invoice_ids[0],
			'view_id': False,
			'views': [(form_id, 'form'), (tree_id, 'tree')],
			'context': "{'type': 'in_invoice'}",
			'type': 'ir.actions.act_window',
		}


