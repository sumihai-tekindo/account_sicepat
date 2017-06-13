from openerp import models, fields, api, _

class data_penerimaan_uang(models.TransientModel):
    _name="data.penerimaan.uang"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    bank_account = fields.Many2one('account.journal', string='Bank Account', required=True)
    account_id = fields.Many2one('account.account', string="Account", required=True)
        
    @api.multi
    def print_report(self,):
        self.ensure_one()
        datas ={}
        mvl_ids = self.env['account.move.line'].search([('date','>=',self.start_date),
                                                      ('date','<=',self.end_date),
                                                      ('journal_id','=',self.bank_account.id),
                                                      ('account_id','=',self.account_id.id),
                                                      
                                                      ('debit','=',0.0),
                                                      ('credit','>',0.0)])
        list_mvl= [mvl.id for mvl in mvl_ids]
        print "xxxxxxdomxxxxxxxxxx",[('date','>=',self.start_date),
                                                      ('date','<=',self.end_date),
                                                      ('journal_id','=',self.bank_account.id),
                                                      ('account_id','=',self.account_id.id),
                                                      
                                                      ('debit','=',0.0),
                                                      ('credit','>',0.0)]
        print "--------------------------------------",list_mvl
        datas={
            'model'    : 'account.move.line',
            "ids"    : list_mvl, #id record dari tabel account.cashback.lines
            'start_date':self.start_date,
            'end_date':self.end_date,
            'bank_account':self.bank_account.id,
            'account_id':self.account_id.id,
        }
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'data.penerimaan.uang.xls',
            'datas': datas
        }