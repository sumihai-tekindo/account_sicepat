import datetime
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from dateutil.relativedelta import relativedelta

class report_bill_monthly_parser(report_sxw.rml_parse):

    def set_context(self, objects, data, ids, report_type=None):
        res = super(report_bill_monthly_parser, self).set_context(objects, data, ids, report_type=report_type)
        self.localcontext.update({
            'get_outstandings': self.get_outstandings,
            })
        return res

    def get_outstandings(self,objects=None,datas=None):
        cr=self.cr
        uid=self.uid
        ids=self.ids
        context={}
        # ids =[94401]
        # print "=====enter zone=======",self.objects
        # for ob in dir(self.objects):
        #     print "=====enter zone=======",ob,"===",eval("self.objects."+ob),""
        
        
        if not objects:
            objects =self.objects
        # print "xxxxxxxxxxxxxxxxxx",type(objects)

        if objects and (objects._name=='res.partner.bill.print.wiz' or objects._name=='res.partner.bill.mail.wiz'):
            ids = objects.partner_ids and [x.id for x in objects.partner_ids]
            partners = objects.partner_ids
        else:
            # if objects.
            #     partners = objects
            # else
                # partners = self.pool.get('res.partner').browse(cr,uid,ids)
            partners = self.pool.get('res.partner').browse(cr,uid,ids)
            
        # print "--sdfsfsd------------",objects
        if not context:context={}
        result = {}
        journal_bank = self.pool.get('account.journal').search(cr,uid,[('type','in',('cash','bank'))])
        journal_invoice = self.pool.get('account.journal').search(cr,uid,[('type','not in',('bank', 'cash', 'purchase', 'purchase_refund'))])
        account_ids = self.pool.get('account.account').search(cr,uid,[('type','=','receivable')])

        today =datetime.datetime.today()
        std =False
        try:
            std = objects.start_date
        except:
            std = False

        if not std and datas:
            try:
                std = datas.get('start_date')
            except:
                std=std
        start_date = {}
        end_date = {}
        # print "===========",partners
        if not std:
            for partner_id in partners:
                if not partner_id.billing_period:
                    start_date.update({partner_id:datetime.date.today().strftime('%Y-%m-%d')})
                    end_date.update({partner_id:datetime.date.today().strftime('%Y-%m-%d')})
                else:
                    if partner_id.billing_period=='weekly':
                        billing_nth_day = partner_id.billing_nth_day

                        # 0 = Monday, 1 = Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
                        curr_week_day = today.weekday()

                        # print "=----------------=>",curr_week_day,"-",billing_nth_day-1

                        if billing_nth_day-1 > curr_week_day:
                            end_date.update({partner_id:today-relativedelta(days=(7-billing_nth_day-1+curr_week_day))})
                        elif billing_nth_day-1==curr_week_day:
                            end_date.update({partner_id:today})
                            start_date.update({partner_id:today-relativedelta(days=7)})
                        else:
                            norm = billing_nth_day-1
                            if norm<0:
                                norm =abs(norm)
                            end_date.update({partner_id:today-relativedelta(days=curr_week_day-norm)})
                            start_date.update({partner_id:end_date.get(partner_id,0)-relativedelta(days=7)})
                    elif partner_id.billing_period=='monthly':
                        monthly_date=datetime.datetime.strptime(partner_id.billing_date,'%Y-%m-%d').strftime('%d')
                        try:
                            new_date = "%s-%s-%s"%(today.strftime('%Y'),today.strftime('%m'),monthly_date)
                        except:
                            try:
                                new_date = "%s-%s-%s"%(today.strftime('%Y'),today.strftime('%m'),'30')
                            except:
                                try:
                                    new_date = "%s-%s-%s"%(today.strftime('%Y'),today.strftime('%m'),'28')
                                except:
                                    new_date = "%s-%s-%s"%(today.strftime('%Y'),today.strftime('%m'),'29')

                        new_end_date = datetime.datetime.strptime(new_date,'%Y-%m-%d')
                        if new_end_date>=today:
                            end_date.update({partner_id:today})
                        else:
                            end_date.update({partner_id:new_end_date})
                        start_date.update({partner_id:end_date.get(partner_id,0) - relativedelta(months=1)})
                    end_date.update({partner_id:end_date.get(partner_id).strftime('%Y-%m-%d')})
                    start_date.update({partner_id:start_date.get(partner_id).strftime('%Y-%m-%d')})
        elif std and objects and not datas:
            for partner_id in partners:
                # print "==============",self.objects
                start_date.update({partner_id:objects.start_date})
                end_date.update({partner_id:objects.end_date})
        elif std and objects and datas:
            # print "==============",datas,type(datas),datas.get('start_date')
            for partner_id in partners:
                start_date.update({partner_id:datas.get('start_date',False)})
                end_date.update({partner_id:datas.get('end_date',False)})

        # print "==========",start_date,"xxxxx",end_date
        for partner_id in partners:
            first_date=False
            last_date=False
            total_inv=0.0
            total_paid=0.0
            total_outstanding=0.0
            
            domain_inv = [
                        ('partner_id', '=', partner_id.id), 
                        ('move_id.state', '=', 'posted'), 
                        ('account_id', 'in', account_ids), 
                        ('journal_id', 'in', journal_invoice), 
                        ('debit', '>', 0), 
                        ('date','>=',start_date.get(partner_id,False)),
                        ('date','<=',end_date.get(partner_id,False)),
                    ]
            domain_payment = [('partner_id','=',partner_id.id),
                    ('account_id', 'in', account_ids) ,('credit','>',0.0),('journal_id','in',journal_bank),('date','>=',start_date.get(partner_id,False)),
                        ('date','<=',end_date.get(partner_id,False))]
            domain_outstandings = [
                        ('partner_id', '=', partner_id.id), 
                        ('move_id.state', '=', 'posted'), 
                        ('account_id', 'in', account_ids), 
                        ('journal_id', 'in', journal_invoice), 
                        ('debit', '>', 0), 
                        ('date','<=',end_date.get(partner_id,False)),
                    ]

            mv_inv_ids = self.pool.get('account.move.line').search(cr,uid,domain_inv,context=context,order="date asc")
            mv_inv = self.pool.get('account.move.line').browse(cr,uid,mv_inv_ids,context=context)

            mv_payment_ids = self.pool.get('account.move.line').search(cr,uid,domain_payment,context=context,order="date asc")
            mv_payment = self.pool.get('account.move.line').browse(cr,uid,mv_payment_ids,context=context)

            mv_outstanding_ids = self.pool.get('account.move.line').search(cr,uid,domain_outstandings,context=context,order="date asc")
            mv_outstanding = self.pool.get('account.move.line').browse(cr,uid,mv_outstanding_ids,context=context)

            date_dict = {}
            payment_dict = {}
            outstanding_dict ={}
            for inv in mv_inv:
                key = inv.date
                if date_dict.get(key,False):
                    date_dict[key]['total']=date_dict.get(key).get('total') + inv.debit
                    
                else:
                    date_dict[key]={
                        'date':inv.date,
                        'total':inv.debit,
                        'currency_id':inv.company_id.currency_id,
                        'due_date':inv.date_maturity,
                        }
                total_inv+= inv.debit
                # if not first_date:
                #     first_date=key
                # last_date=key

            for pay in mv_payment:
                key = pay.date
                if payment_dict.get(key,False):
                        payment_dict[key]['total']=payment_dict.get(key).get('total') + pay.credit-pay.amount_residual
                else:
                    payment_dict[key]={
                        'date':pay.date,
                        'total':pay.credit-pay.amount_residual,
                        'currency_id':pay.company_id.currency_id,
                        'payment_date':pay.date,
                        }
                total_paid+=pay.credit-pay.amount_residual

            for out in mv_outstanding:
                key = out.date
                if outstanding_dict.get(key,False):
                    outstanding_dict[key]['total']+=out.amount_residual
                    
                else:
                    outstanding_dict[key]={
                        'date':out.date,
                        'total':out.amount_residual,
                        'currency_id':out.company_id.currency_id,
                        'due_date':out.date_maturity,
                        }
                total_outstanding+=out.amount_residual
                if not first_date:
                    first_date=key
                last_date=key
            

        
            result.update({
                partner_id:{
                    'start_date':start_date.get(partner_id,False),
                    'end_date':end_date.get(partner_id,False),
                    'start_date_outstanding':first_date,
                    'invoices': date_dict,
                    'invoices_total':total_inv,
                    'payment': payment_dict,
                    'payment_total':total_paid,
                    'outstandings' : outstanding_dict,
                    'outstandings_total': total_outstanding,
                    'currency_id': partner_id.company_id.currency_id
                    }
                })
        return result

class report_bill_monthly_report_per_customer(osv.AbstractModel):
    _name = 'report.customer_bill_mail.bill_monthly_report_per_customer'
    _inherit = 'report.abstract_report'
    _template = 'customer_bill_mail.bill_monthly_report_per_customer'
    _wrapped_report_class = report_bill_monthly_parser
