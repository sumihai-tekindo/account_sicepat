
from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from openerp import models, api


def str_to_datetime(strdate):
	return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class asset_building_cost(osv.Model):
	_name = 'asset.building.cost'
	_description = 'Cost related to a building'
	_order = 'date desc, building_id asc'


	_columns = {
		'name': fields.related('building_id', 'name', type="char", string='Name', store=True),
		'building_id': fields.many2one('account.analytic.account', 'Building'),
		'cost_subtype_id': fields.many2one('asset.service.type', 'Type', help='Cost type purchased with this cost'),
		'amount': fields.float('Total Price'),
		'cost_type': fields.selection([('contract', 'Rental'), ('services','Services'), ('fuel','Fuel'), ('other','Other')], 'Category of the rent', help='For internal purpose only', required=True),
		'parent_id': fields.many2one('asset.building.cost', 'Parent', help='Parent cost to this current cost'),
		'cost_ids': fields.one2many('asset.building.cost', 'parent_id', 'Included Services'),
		'date' :fields.date('Date',help='Date when the cost has been executed'),
		'cost_id': fields.many2one('asset.building.cost', 'Cost',  ondelete='cascade'),
		'contract_id': fields.many2one('asset_building.log.contract', 'Contract', help='Contract attached to this cost'),
		'auto_generated': fields.boolean('Automatically Generated', readonly=True, required=True),
	}

	_defaults ={
		'cost_type': 'contract',
	}

class asset_service_type(osv.Model):
	_name = 'asset.service.type'
	_description = 'Type of services available on a asset'
	_columns = {
		'name': fields.char('Name', required=True, translate=True),
		'category': fields.selection([('rent', 'Rent'), ('service', 'Service'), ('both', 'Both')], 'Category', required=True, help='Choose wheter the service refer to contracts, building services or both'),
	}

class asset_rental(osv.Model):
	# _inherits = {'asset.building.cost': 'cost_id'}
	_name = 'asset.rental'
	_description = 'Contract information on a building'
	_order='state desc,expiration_date'

	

	def run_scheduler(self, cr, uid, context=None):
		self.scheduler_manage_auto_costs(cr, uid, context=context)
		self.scheduler_manage_contract_expiration(cr, uid, context=context)
		return True

	

	def compute_next_year_date(self, strdate):
		oneyear = datetime.timedelta(days=365)
		curdate = str_to_datetime(strdate)
		return datetime.datetime.strftime(curdate + oneyear, tools.DEFAULT_SERVER_DATE_FORMAT)

	def on_change_start_date(self, cr, uid, ids, strdate, enddate, context=None):
		if (strdate):
			return {'value': {'expiration_date': self.compute_next_year_date(strdate),}}
		return {}

	def get_days_left(self, cr, uid, ids, prop, unknow_none, context=None):
	  
		res = {}
		for record in self.browse(cr, uid, ids, context=context):
			if (record.expiration_date and (record.state == 'open' or record.state == 'toclose')):
				#today = str_to_datetime(time.strftime(tools.DEFAULT_SERVER_DATE_FORMAT))
				startdate = str_to_datetime(record.start_date)
				renew_date = str_to_datetime(record.expiration_date)
				diff_time = (renew_date-startdate).days
				res[record.id] = diff_time > 0 and diff_time or 0
			else:
				res[record.id] = -1
		return res

	def get_count_month(self, cr, uid, ids, prop, unknow_none, context=None):
	
		res = {}
		for record in self.browse(cr, uid, ids, context=context):
			if (record.expiration_date and (record.state == 'open' or record.state == 'toclose')):
				today = str_to_datetime(time.strftime(tools.DEFAULT_SERVER_DATE_FORMAT))
				renew_date = str_to_datetime(record.expiration_date)
				start_date = str_to_datetime(record.start_date)
				diff_time = (renew_date-start_date)
				end_month = renew_date.month
				start_month = start_date.month
				diff_month = end_month - start_month
				end_year = renew_date.year
				start_year = start_date.year
				diff_year = end_year - start_year
				if diff_year :
					diff_month = diff_year*12+diff_month
				
				res[record.id] = diff_month > 0 and diff_month or 0
			else:
				res[record.id] = -1
		return res 

	def act_renew_contract(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'toclose'}, context=context)
		assert len(ids) == 1, "This operation should only be done for 1 single contract at a time, as it it suppose to open a window as result"
		for element in self.browse(cr, uid, ids, context=context):
			#compute end date
			startdate = str_to_datetime(element.start_date)
			enddate = str_to_datetime(element.expiration_date)
			diffdate = (enddate - startdate)
			default = {
				'date': fields.date.context_today(self, cr, uid, context=context),
				'start_date': datetime.datetime.strftime(str_to_datetime(element.expiration_date) + datetime.timedelta(days=1), tools.DEFAULT_SERVER_DATE_FORMAT),
				'expiration_date': datetime.datetime.strftime(enddate + diffdate, tools.DEFAULT_SERVER_DATE_FORMAT),
			}
			newid = self.pool.get(self._name).copy(cr, uid, element.id, default, context=context)
		mod, modid = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'maintenance_building', 'asset_building_log_contract_form')
		return {
			'name':_("Renew Contract Building"),
			'view_mode': 'form',
			'view_id': modid,
			'view_type': 'tree,form',
			'res_model': self._name,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'domain': '[]',
			'res_id': newid,
			'context': {'active_id':newid}, 
		}

	
	def contract_close(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'closed'}, context=context)

	def contract_open(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'open'}, context=context)


	def _computedate(self,cr,uid,ids,name,args,context=None):
		res = {}
		for fleet in self.browse(cr,uid,ids):
			res[fleet['id']]=(datetime.date.today()+relativedelta(months=1)).strftime('%Y-%m-%d')
		return res

	def onchange_expired(self,cr,uid,ids,cost_frequency,start_date,context=None):
		expiration_date = datetime.datetime.today()
		if cost_frequency and cost_frequency != 'no':
			expiration_date = datetime.datetime.strptime(start_date,'%Y-%m-%d') + _intervalTypes[cost_frequency]

		return {'value': {'expiration_date': expiration_date.strftime('%Y-%m-%d')}}


	def document_complete(self,cr,uid,ids,context=None):
		return self.write(cr, uid, ids, {'state': 'completed'}, context=context)

	def get_total(self,cr,uid,ids,name,args,context=None):
		res = {}
		for rental_id in self.browse(cr,uid,ids):
			res[rental_id['id']] = rental_id.deposit + rental_id.biaya_sewa
		return res

	def _get_name(self, cr, uid, ids, prop, unknow_none, context=None):
		res = {}
		for record in self.browse(cr, uid, ids, context=context):
			name = record.building_type
			# name += ' / '+ record.date
			# if record.building_type:
			#     name += ' / '+ record.cost_subtype_id.name
			# if record.date:
			#     name += ' / '+ record.date
			res[record.id] = name
		return res
	###ADD queue to supplier invoice


	def compute_rent(self, cr, uid, ids, context=None):
		record = self.browse(cr, uid, ids)
		account_id =0
		amount=0
		#if record.invoice_id:
		sewa=True
		start_date=record.start_date
		end_date1=record.expiration_date
		account_analytic_id=record.branch.id
		#Fill to the form
		vals={
			'type':'in_invoice',
			'partner_id':record.insurer_id.id,
			'account_id':record.insurer_id.property_account_payable.id,
			'currency_id':record.insurer_id.company_id.currency_id.id,
			'department_id':record.department_id.id,
			'date_invoice':record.date,
			'sewa':True,
			'date_start':record.start_date,
			'date_end':record.expiration_date,
			'aset_rental_id': record.id,
			}
		#Fill to the lINE
		account=self.pool.get('account.invoice').create(cr, uid, vals,context=context) 

		product=record.product_id
		to_line = {record.product_id:record.biaya_sewa, record.product_deposit:record.deposit}
		for prod, price in to_line.items():
			if prod and price :
					self.pool.get('account.invoice.line').create(cr, uid, {
						'product_id':prod.id, 
						'invoice_id':account, 
						'name':prod.name_template,
					 	'account_analytic_id' :account_analytic_id,
						'account_id':prod.property_account_expense and prod.property_account_expense.id or (prod.categ_id.property_account_expense_categ and prod.categ_id.property_account_expense_categ.id),
						'quantity':1,
						'uos_id':prod.uom_id.id,
						'price_unit':price,
					},context=context)
		record.invoice_id=True


	
	def return_supplier_invoice(self, cr, uid, ids, insurer_id,context=None):
		domain = [('aset_rental_id','in',ids)]
		invoice_ids = self.pool.get('account.invoice').search(cr,uid,domain)
		context_domain = [('id','in',invoice_ids)]
		return {
			'type': 'ir.actions.act_window',
			'name': 'Supplier Invoice',
			'res_model': 'account.invoice',
			'view_type': 'form',
			'view_mode': 'tree',
			'res_id': invoice_ids,
			'target': 'current',
			'domain': domain,
			'nodestroy': True,
			'flags': {'form': {'action_buttons': True}}
			}

			
	def _count_supplier_invoice(self, cr, uid, ids, field_name, arg, context=None):
		result = {}
		invoice_ids = self.pool.get('account.invoice').search(cr,uid,[('aset_rental_id','in',ids)])
		#invoices = self.pool.get('account.invoice').browse(cr,uid,invoice_ids)

		count_invoice = len(invoice_ids) if invoice_ids else 0
	
		
		for record in self.browse(cr, uid, ids, context=context):
			result[record.id] = count_invoice
		return result

	def on_change_start_date(self, cr, uid, ids, strdate, enddate, context=None):
		if (strdate):
			return {'value': {'expiration_date': self.compute_next_year_date(strdate),}}
		return {}

	def _change(self,cr,uid,is_deposit,product_deposit,deposit,context=None):
		if (is_deposit)==True:	
			(product_deposit)==True
			(deposit)==True
		else:
			(product_deposit)==False
			(deposit)==False		


	_columns = {
		'name': fields.function(_get_name, type="text", string='Name', store=True),
		'start_date': fields.date('Contract Start Date', help='Date when the coverage of the contract begins'),
		'expiration_date': fields.date('Contract Expire Date', help='Date when the coverage of the contract expirates (by default, one year after begin date)'),
		'date': fields.date('Invoice Date', help='Date when the coverage of the contract begins'),
		'days_left': fields.function(get_days_left, type='integer', string='Warning Date'),
		'insurer_id': fields.many2one('res.partner', 'Supplier'),
		# 'invoice_id':fields.boolean(default=False, copy=False),
		'purchaser_id': fields.many2one('res.partner', 'Contractor', help='Person to which the contract is signed for'),
		'ins_ref': fields.char('Contract Reference', size=64, copy=False),
		'state': fields.selection([('open', 'In Progress'), ('toclose','To Close'), ('completed','Document Completed'),('closed', 'Terminated')],
								  'Status', readonly=True, help='Choose wheter the contract is still valid or not',
								  copy=False),
		'branch' : fields.many2one('account.analytic.account','Branch'),
		'alamat' : fields.text('Address'),
		'deposit' : fields.float('Deposit'),
		# 'is_deposit': fields.function(_change,'Deposit', readonly=False, default=False),
		'is_deposit': fields.boolean('Deposit', default=False),
		'biaya_sewa' : fields.float('Biaya Sewa'),
		'total' : fields.function(get_total, 'Total',readonly=True),
		'date_computation': fields.function(_computedate,string='Computation',type="date",store=True),
		'product_id' : fields.many2one('product.product','COA Sewa',required=True),
		'product_deposit' : fields.many2one('product.product','COA Deposit'),
		'get_count_month' : fields.function(get_count_month, type='integer',string="Month",readonly=True),
		'building_type' : fields.selection([('head_office','Head Office'), 
											('region', 'Region'), 
											('provinsi','Provinsi'), 
											('kota','Kabupaten/Kota'),
											('gerai','Gerai'), 
											('toko','Toko'),
											('cabang','Cabang'),
											('transit','Transit'),
											('agen','Agen'),
											('pusat_transitan','Pusat Transitan'),
											('perwakilan','Perwakilan'),
											('other','Lainnya')], 
											'Type'),
		'building_id': fields.many2one('account.analytic.account', 'Building'),
		'notes': fields.text('Terms and Conditions', help='Write here all supplementary informations relative to this contract', copy=False),
		'cost_generated': fields.float('Recurring Cost Amount', help="Costs paid at regular intervals, depending on the cost frequency. If the cost frequency is set to unique, the cost will be logged at the start date"),
		'cost_frequency': fields.selection([('no','No'), 
											('daily', 'Daily'), 
											('weekly','Weekly'), 
											('monthly','Monthly'),
											('6months','6 Months'), 
											('yearly','Yearly'),
											('2years','2 Years'),
											('5years','5 Years')], 
											'Recurring Cost Frequency', help='Frequency of the recuring cost'),
		'generated_cost_ids': fields.one2many('asset.building.cost', 'contract_id', 'Generated Costs'),
		# 'sum_cost': fields.function(_get_sum_cost, type='float', string='Indicative Costs Total'),
		'department_id' : fields.many2one('account.invoice.department','Department',required=True),
		'cost_id': fields.many2one('asset.building.cost', 'Cost', ondelete='cascade'),
		'invoice_id':fields.boolean(default=False, copy=False),
		'count_invoice' : fields.function(_count_supplier_invoice,string='Invoice'),
		'cost_amount': fields.related('cost_id', 'amount', string='Amount', type='float'), #we need to keep this field as a related with store=True because the graph view doesn't support (1) to address fields from inherited table and (2) fields that aren't stored in database
		
	}

	_defaults = {
		'purchaser_id': lambda self, cr, uid, ctx: self.pool.get('res.users').browse(cr, uid, uid, context=ctx).partner_id.id or False,
		'date': fields.date.context_today,
		'start_date': fields.date.context_today,
		'state':'open',
		# 'expiration_date': lambda self, cr, uid, ctx: self.compute_next_year_date(fields.date.context_today(self, cr, uid, context=ctx)),
		'cost_frequency': 'no',
		# 'cost_subtype_id': _get_default_contract_type,
		'cost_type': 'contract',
	}

	


class asset_contract_state(osv.Model):
	_name = 'asset.contract.state'
	_description = 'Contains the different possible status of a leasing contract'

	_columns = {
		'name':fields.char('Contract Status', required=True),
	}

	