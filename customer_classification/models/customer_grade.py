from openerp import models, fields, api, _
import mx.DateTime as dt
from openerp.exceptions import except_orm, Warning, RedirectWarning
import datetime

class master_cust_grade(models.Model):
	_name = "master.cust.grade"

	name = fields.Char("Grade Name",required=True)
	code = fields.Char("Code",required=False)
	
	grade_type_id = fields.Many2one("master.cust.grade.type","Grade Type", required=True)
	percentage_disc = fields.Float("Discount Percentage", required=True)
	# python_rule = fields.Text("Rule")
	grade_rule_ids = fields.One2many('master.cust.grade.rules','grade_id','Grade Rules')


_default_rule = """# applicable variables are :
# grade = browsable object of partner.grade.calc , 
# partner = partner object ,
# current_discount = current_discount in partner,
# grade_type = customer grade type,
# applicable_partners = rule applicable partners,
# grade_start & grade_end = grade start date & grade end date,
# rule_start & rule_end = rule start & end date,
# rule = browsable object of current grade rule
# 
True"""
class master_cust_grade_rules(models.Model):
	_name 				= "master.cust.grade.rules"
	_order 				= "grade_id asc, sequence desc"

	start 				= fields.Date("Date Start")
	end 				= fields.Date("Date End")
	min_rev 			= fields.Float("Min. Revenue",required=False)
	max_rev 			= fields.Float("Max. Revenue",required=False)
	r_type 				= fields.Selection([("standard","Standard"),("custom","Custom")],"Rule Type")
	python_rule 		= fields.Text("Python Rule",
						default=_default_rule)

	active 				= fields.Boolean("Active",default=True)
	grade_id 			= fields.Many2one("master.cust.grade","Grade Name")
	partner_ids			= fields.Many2many('res.partner','grade_rule_partner_rel','rule_id','partner_id',"Applicable Partners")
	sequence        	= fields.Integer("Sequence",help="Higher Sequence is most top priority")
	override_disc   	= fields.Float("Override Discount")

class master_cust_grade_type(models.Model):
	_name 				= "master.cust.grade.type"

	name 				= fields.Char("Grade Type", required=True)
	description 		= fields.Char("Description")

class partner_grade_calculation(models.Model):
	_name = "partner.grade.calc"

	name 				= fields.Char("Grade Statement Number",required=True,default="/")
	start_date 			= fields.Date("Start Date", help="Start Date of Revenue",required=True)
	end_date 			= fields.Date("End Date", help="End Date of Revenue",required=True)
	grade_calc_ids 		= fields.One2many("partner.grade.calc.line",'cust_grade_id',"Customer Grades to Approve")
	valid_start_date	= fields.Date("Valid start date")
	valid_end_date		= fields.Date("Valid end date")
	state				= fields.Selection([('draft','Draft'),('submitted','Submitted'),('review','To Review'),('approved','Approved')],"State",default='draft')

	@api.multi
	def submit(self):
		self.ensure_one()
		line_ids = []
		numbers = {
			'draft' : 0,
			'draft_ids':[],
			'submitted' : 0,
			'submitted_ids':[],
			'review' : 0,
			'review_ids':[],
			'approved' : 0,
			'approved_ids':[],
			}
		for l in self.grade_calc_ids:
			curr = numbers.get(l.state,0)
			curr+=1
			curr_ids = numbers.get(l.state+'_ids',[])
			curr_ids.append(l.id) 
			numbers.update({
				l.state:curr,
				l.state+'_ids':curr_ids
				})
		if numbers.get('draft_ids',False):
			recs = self.env['partner.grade.calc.line'].search([('id','in',numbers.get('draft_ids'))])
			recs.write({'state':'submitted'})
		next_sequence = self.pool['ir.sequence'].next_by_code(self._cr,self._uid,'partner_grade_seq') or "/"
		# print "============next_sequence============",next_sequence
		self.write({'state':'submitted','name':next_sequence})

	@api.multi
	def review(self):
		self.ensure_one()
		line_ids = []
		numbers = {
			'draft' : 0,
			'draft_ids':[],
			'submitted' : 0,
			'submitted_ids':[],
			'review' : 0,
			'review_ids':[],
			'approved' : 0,
			'approved_ids':[],
			}
		for l in self.grade_calc_ids:
			curr = numbers.get(l.state,0)
			curr+=1
			curr_ids = numbers.get(l.state+'_ids',[])
			curr_ids.append(l.id) 
			numbers.update({
				l.state:curr,
				l.state+'_ids':curr_ids
				})
		if numbers.get('submitted_ids',False):
			recs = self.env['partner.grade.calc.line'].search([('id','in',numbers.get('submitted_ids'))])
			recs.write({'state':'review'})
		self.write({'state':'review'})

	@api.multi
	def approved(self):
		self.ensure_one()
		line_ids = []
		numbers = {
			'draft' : 0,
			'draft_ids':[],
			'submitted' : 0,
			'submitted_ids':[],
			'review' : 0,
			'review_ids':[],
			'approved' : 0,
			'approved_ids':[],
			}
		for l in self.grade_calc_ids:
			curr = numbers.get(l.state,0)
			curr+=1
			curr_ids = numbers.get(l.state+'_ids',[])
			curr_ids.append(l.id) 
			numbers.update({
				l.state:curr,
				l.state+'_ids':curr_ids
				})
		if numbers.get('submitted_ids',False):
			recs = self.env['partner.grade.calc.line'].search([('id','in',numbers.get('submitted_ids'))])
			recs.write({'state':'approved'})
		self.write({'state':'approved'})

	@api.multi
	def import_customer(self):
		self.ensure_one()
		dt_start_date = dt.strptime(self.start_date,'%Y-%m-%d')
		dt_end_date = dt.strptime(self.end_date,'%Y-%m-%d')
		# dt_diff = dt_end_date-dt_start_date

		dt_diff=dt.Age(dt_end_date,dt_start_date)
		prev_start_date = (dt_start_date - dt_diff).strftime('%Y-%m-%d')
		prev_end_date = (dt_end_date - dt_diff).strftime('%Y-%m-%d')
		query = """
				SELECT dummy.*,
				rp.current_discount as curr_disc_percent
				FROM (
					SELECT 
						coalesce(s1.partner_id,s2.partner_id) as partner_id,
						sum(coalesce(s2.curr_rev_bef_revision,0.00)) as prev_rev_bef_revision,
						round(sum(coalesce(s2.curr_rev_bef_revision,0.00))/%s,2) as prev_rev_bef_revision_avg,
						sum(coalesce(s2.curr_revision,0.00)) as prev_revision,
						round(sum(coalesce(s2.curr_revision,0.00))/%s,2) as prev_revision_avg,
						sum(coalesce(s2.curr_net_rev,0.00)) as prev_revenue, 
						round(sum(coalesce(s2.curr_net_rev,0.00))/%s,2) as prev_revenue_avg,
						sum(coalesce(s1.curr_rev_bef_revision,0.00)) as curr_rev_bef_revision,
						round(sum(coalesce(s1.curr_rev_bef_revision,0.00))/%s,2) as curr_rev_bef_revision_avg,
						sum(coalesce(s1.curr_revision,0.00)) as curr_revision,
						round(sum(coalesce(s1.curr_revision,0.00))/%s,2) as curr_revision_avg,
						sum(coalesce(s1.curr_net_rev,0.00)) as curr_revenue, 
						round(sum(coalesce(s1.curr_net_rev,0.00))/%s,2) as curr_revenue_avg
					FROM cust_grade_statistics s1
					FULL OUTER JOIN cust_grade_statistics s2 on s2.partner_id=s1.partner_id 
						and s2.period_start>'%s' and s2.period_end<'%s'					
					where s1.period_start>='%s' and s1.period_end<='%s'

					group by s1.partner_id,s2.partner_id
					) dummy
				LEFT JOIN res_partner rp on rp.id=dummy.partner_id
				"""%(abs(dt_diff.months),abs(dt_diff.months),abs(dt_diff.months),abs(dt_diff.months),abs(dt_diff.months),abs(dt_diff.months),
						prev_start_date,prev_end_date,self.start_date,self.end_date)
		# print "xxxxxxxxxxxxxxxxxxxxxxxxx",dt_diff.months
		self._cr.execute(query)
		res =self._cr.dictfetchall()
		for r in res:
			new_value={}
			new_value.update({
						'cust_grade_id':self.id,
						'partner_id': r['partner_id'],
						'valid_start_date': self.valid_start_date,
						'valid_end_date': self.valid_end_date,
						'prev_start':prev_start_date,
						'prev_end':prev_end_date,
						'curr_start':self.start_date,
						'curr_end':self.end_date,

						'curr_disc_percent':r['curr_disc_percent'],

						'prev_rev_bef_revision':r['prev_rev_bef_revision'],
						'prev_rev_bef_revision_avg':r['prev_rev_bef_revision_avg'],
						'prev_revision':r['prev_revision'],
						'prev_revision_avg':r['prev_revision_avg'],
						'prev_revenue':r['prev_revenue'],
						'prev_revenue_avg':r['prev_revenue_avg'],

						'curr_rev_bef_revision':r['curr_rev_bef_revision'],
						'curr_rev_bef_revision_avg':r['curr_rev_bef_revision_avg'],
						'curr_revision':r['curr_revision'],
						'curr_revision_avg':r['curr_revision_avg'],
						'curr_revenue':r['curr_revenue'],
						'curr_revenue_avg':r['curr_revenue_avg'],

						'disc_proposed':0.0,
						'disc_approved':0.0,
						'grade_proposed_id':False,
						'notes':False,
						'state':'draft'
						})
			self.env['partner.grade.calc.line'].create(new_value)
		return True

	@api.multi
	def calculate_grade(self):
		self.ensure_one()
		grades = self.env['master.cust.grade'].search([])
		dict_grade = {}
		for g in grades :
			if g.grade_type_id.id in dict_grade:
				curr_g = dict_grade.get(g.grade_type_id.id,[])
			else:
				curr_g = []
			curr_g.append(g)
			dict_grade.update({g.grade_type_id.id:curr_g})

		
		for line in self.grade_calc_ids:
			grade = line.cust_grade_id
			disc_proposed = 0.0
			grade_proposed_id = False
			if line.partner_id.grade_type_id and line.partner_id.grade_type_id.id:
				partner = line.partner_id
				current_discount = line.curr_disc_percent
				grade_type = line.partner_id.grade_type_id and line.partner_id.grade_type_id.id or False
				grade_start = datetime.datetime.strptime(grade.start_date,'%Y-%m-%d')
				grade_end = datetime.datetime.strptime(grade.end_date,'%Y-%m-%d')
				if grade_type:
					for master_grade in dict_grade.get(grade_type,[]):
						for rule in master_grade.grade_rule_ids:
							applicable_partners = [x.id for x in rule.partner_ids]
							rule_start = rule.start and datetime.datetime.strptime(rule.start,'%Y-%m-%d') or False
							rule_end = rule.end and datetime.datetime.strptime(rule.end,'%Y-%m-%d') or False
							condition = False
							try:
								condition = eval(rule.python_rule)
							except:
								raise except_orm(_('Error!'), _('Python rule is misconfigured for rule %s in Grade Type %s \n of Grade : %s'%(rule.id,grade.grade_type_id.name,grade.name)))
							if condition:
								disc_proposed=master_grade.percentage_disc
								disc_proposed = rule.override_disc
								grade_proposed_id = rule.grade_id.id
								break
			line.write({'disc_proposed':disc_proposed,'grade_proposed_id':grade_proposed_id})

		return True

class partner_grade_calculation_line(models.Model):
	_name = "partner.grade.calc.line"

	cust_grade_id 		= fields.Many2one("partner.grade.calc","Grade Statement")
	partner_id 			= fields.Many2one("res.partner","Customer")
	valid_start_date	= fields.Date("Valid start date")
	valid_end_date		= fields.Date("Valid end date")
	curr_disc_percent	= fields.Float("Current Disc (%)")

	prev_start 			= fields.Date("Prev. Start", help="Start Date of Revenue",required=True)
	prev_end 			= fields.Date("Prev. End", help="End Date of Revenue",required=True)
	curr_start 			= fields.Date("Curr. Start", help="Start Date of Revenue",required=True)
	curr_end 			= fields.Date("Curr. End", help="End Date of Revenue",required=True)
	
	prev_rev_bef_revision = fields.Float("Prev. Revenue before revision") 
	prev_rev_bef_revision_avg 	= fields.Float("Prev. Avg. Rev.\nBefore Revision")
	prev_revision 		= fields.Float("Prev. Revision") 
	prev_revision_avg 	= fields.Float("Prev. Avg. Revision")
	prev_revenue 		= fields.Float("Prev. Revenue")
	prev_revenue_avg 	= fields.Float("Prev. Avg. Revenue")
	
	curr_rev_bef_revision = fields.Float("Curr. Revenue \nbefore revision") 
	curr_rev_bef_revision_avg 	= fields.Float("Curr. Avg. Revenue before revision")
	curr_revision 		= fields.Float("Curr. Revision") 
	curr_revision_avg 	= fields.Float("Curr. Avg. Revision")
	curr_revenue 		= fields.Float("Curr. Revenue")
	curr_revenue_avg 	= fields.Float("Curr. Avg. Revenue")

	disc_proposed		= fields.Float("Disc. Proposed (%)")
	disc_approved		= fields.Float("Disc. Approved (%)")
	grade_proposed_id   = fields.Many2one("master.cust.grade","Grade Proposed")
	grade_approved_id   = fields.Many2one("master.cust.grade","Grade Approved")
	sales_id			= fields.Many2one('res.users', string='Sales Person', related='partner_id.user_id', store=False, readonly=True, help="Sales Person Name")
	cro_id				= fields.Many2one("res.users",string='CRO Users', related='partner_id.followup_responsible_id', store=False, readonly=True, help="CRO User")
	notes				= fields.Text("Notes")
	state				= fields.Selection([('draft','Draft'),('submitted','Submitted'),('review','To Review'),('approved','Approved')],"State",default='draft')
