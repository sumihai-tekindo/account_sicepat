from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from datetime import date
import pymssql


class bi_report_wizard(osv.osv_memory):
	_name = "bi.report.wizard"

	_columns = {
	"report_type"	: fields.selection(
		[
		('revenue_sales','Revenue per Sales'),
		('pickup','Pickup'),
		('pengantaran','Pengantaran'),
		],"Jenis Laporan",required=True),

	"start_date"	: fields.date("Start Date" ,required=True),
	"end_date"		: fields.date("End Date" ,required=True),
	}

	_defaults = {
		"report_type":'revenue_sales',
		'start_date':date.today().strftime('%Y-%m-01'),
        'end_date':date.today().strftime('%Y-%m-%d'),	
	}


	def proses_report(self,cr,uid,ids,context=None):
		wiz = self.browse(cr,uid,ids,context=context)[0]
		report_type = wiz.report_type
		start_date = wiz.start_date
		end_date = wiz.end_date
		receivables = []
		locations = []

		if report_type == 'revenue_sales' :
			bi_revenue_obj   =  self.pool.get('bi.revenue.sales.rpt') 
			num = 0;

			cr.execute("delete from bi_revenue_sales_rpt");

			cr.execute("select b.account_analytic_id,a.user_id,a.partner_id,a.state,d.date as joindate, \
			a.date_invoice,b.discount,f.location,f.name as store,  \
			case  \
			when c.name is null then 'Regular' \
			when c.name = 'Darat' then 'Cargo' \
			when c.name != 'Darat' and c.name is not null then c.name \
			end as layanan, \
			case when a.type = 'out_invoice' then sum(b.price_subtotal) else -sum(b.price_subtotal) end as net_revenue , \
			case when a.type = 'out_refund' then sum(b.price_subtotal) end as refund, \
			case when a.type = 'out_invoice' then sum((b.price_unit * b.discount)/100) else 0 end as discount_amount, \
			case when a.type = 'out_invoice' then sum(b.price_subtotal + ((b.price_unit * b.discount)/100)) else 0 end as gross_revenue, \
			sum(case when b.id is not Null then 1 else 0 end)as package, \
			sum(b.quantity)as weight \
			from account_invoice a \
			left join account_invoice_line b on a.id = b.invoice_id \
			left join consignment_service_type c on c.id = b.layanan \
			left join res_partner d on d.id = a.partner_id \
			left join bi_toko f on f.code = d.rds_code \
			where a.type in ('out_invoice','out_refund')and a.state in ('open','paid') and a.date_invoice >= %s and a.date_invoice <= %s and b.cashback_line_id is null \
			group by c.name,a.date_invoice,a.type,b.account_analytic_id,a.user_id,a.partner_id,b.discount,a.state,d.date,f.location,f.name",(start_date,end_date,))


			for res in cr.dictfetchall():
				gerai = '';
				user_id = '';
				partner_id = '';
				package = 0;
				weight = 0;
				gross_amount = 0;
				disc = 0;
				discount = 0;
				refund = 0;
				net_revenue = 0;
				state = '';
				tipe = '';
				layanan = '';
				location = '';
				store = '';

				date_invoice = res['date_invoice']
				joindate = res['joindate']
				gerai = res['account_analytic_id']
				user_id = res['user_id']
				partner_id = res['partner_id']
				package = res['package']
				weight = res['weight']
				gross_revenue = res['gross_revenue']
				net_revenue = res['net_revenue']
				refund = res['refund']
				disc = res['discount']
				discount_amount = res['discount_amount']
				state = res['state']
				# tipe = res['type']
				layanan = res['layanan']
				location = res['location']
				store = res['store']

				if (joindate >= start_date) and (joindate >= start_date) :
					first_invoice = True;
				else :
					first_invoice = False;

				# print 'xxxxxx_gerai',date_invoice,gerai,user_id,partner_id,package,weight,gross_revenue,disc,discount_amount,net_revenue,state,tipe,layanan,location,first_invoice,store;
				print 'xxxxxx_gerai',date_invoice,net_revenue;

				bi_revenue_obj.create(cr, uid, {
					'invoice_date': date_invoice,
					'joindate': joindate,
					'gerai': gerai,
					'user_id': user_id,
					'partner_id': partner_id,
					'package': package,
					'weight': weight,
					'gross_amount': gross_revenue,
					'disc': disc,
					'discount': discount_amount,
					'refund': refund,
					'net_revenue': net_revenue,
					'state': state,
					# 'type': tipe,
					'layanan': layanan,
					'first_invoice': first_invoice,
					'location': location,
					'store': store,
				})



			result = self.pool.get('ir.model.data').get_object_reference(cr,uid,'business_intellegence', 'action_bi_revenue_sales_rpt')
			res_id = result and result[1] or False
			result = self.pool.get('ir.actions.act_window').browse(cr,uid,[res_id]).read()[0]

			return result

		# if report_type == 'pickup' :
		# 	print 'xxxxxxxxxxxxxxxxxxxxxxxxxx_Pickup';

		# # 	conn = pymssql.connect(server=config.host, user=config.username, password=config.password, port=str(config.port), database=config.database)
	 # #        cr_mssql = conn.cursor(as_dict=True)

	 # #        cr_mssql.execute(query,params)
	 # #        records = cr_mssql.fetchall()
	 # #        conn.close()
	 # #        result=[]
	 # #        for record in records:
	 # #            print "===============",record['nohp']

		# if report_type == 'pengantaran' :
		# 	print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx_Pengantaran';


