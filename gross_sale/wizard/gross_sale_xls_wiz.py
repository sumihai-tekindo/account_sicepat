from openerp import api, fields, models

class gross_sale_wizard(models.TransientModel):
    _name = 'gross.sale.wizard'

    date_from = fields.Date(string="Date From", default=lambda self: fields.Date.context_today(self))
    date_to = fields.Date(string="Date To", default=lambda self: fields.Date.context_today(self))

    @api.multi
    def generate_gross_sale(self,):
        self.ensure_one()
        journals=self.env['account.journal'].search([('type','in',['sale','sale_refund'])])
        invoices=self.env['account.invoice'].search([('date_invoice','>=',self.date_from),('date_invoice','<=',self.date_to),('journal_id','in',[j.id for j in journals])])
        
        datas = {
            'model':'account.invoice',
            'form':{
                'date_from':self.date_from,
                'date_to':self.date_to,
            },
            'ids':[inv.id for inv in invoices]
        }

        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'gross.sale.xls',
                'datas': datas,
            }
