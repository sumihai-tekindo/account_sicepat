from openerp import api, fields, models

class stock_wizard(models.TransientModel):
    _name = "stock.move.xls.wiz"

    location_id = fields.Many2one('stock.location', string = 'Source Location', required = True)
    location_dest_id = fields.Many2one('stock.location', string = 'Source Destination', required = True)
    start_date = fields.Date(default=fields.Date.today)
    end_date = fields.Date(default=fields.Date.today)


    @api.multi
    def print_report(self,):
        self.ensure_one()
        datas ={}
        stock_ids = self.env['stock.move'].search([('date_expected','>=',self.start_date),('date_expected','<=',self.end_date), ('state','=','done'),('location_id','=',self.location_id.id),('location_dest_id','=',self.location_dest_id.id)], order = 'location_id, location_dest_id, date_expected, account_analytic_dest_id')
        stock_ids= [move.id for move in stock_ids]
        datas={
            'model': 'stock.move',
            "ids": stock_ids, #id record dari tabel account.cashback.lines
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'stock.move.xls',
            'datas': datas
        }
