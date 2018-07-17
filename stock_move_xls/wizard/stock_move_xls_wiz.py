from openerp import api, fields, models

class stock_wizard(models.TransientModel):
    _name = "stock.move.xls.wiz"

    location_id = fields.Many2one('stock.location', string = 'Source Location', required = True)
    location_dest_id = fields.Many2one('stock.location', string = 'Source Destination', required = True)
    account_analytic_dest_id = fields.Many2one('account.analytic.account', string = 'Nama Cabang')
    product_ids = fields.Many2many('product.product', string = 'Product')
    start_date = fields.Date(default=fields.Date.today)
    end_date = fields.Date(default=fields.Date.today)
    date_of_transfer = fields.Boolean()

    @api.multi
    def print_report(self, ):
        self.ensure_one()
        datas = {}
        picking = self.env['stock.picking'].search([('origin', '!=', False)])
        product_ids = [p.id for p in self.product_ids]
        clause_1 = [
            ('state', '=', 'done'),
            ('picking_id.name', 'not in', [p.origin for p in picking]),
            #('picking_id.name', 'not in', tuple([p.origin for p in picking]))
            #'picking_id.name', NOT LIKE, ('ISSU%')),
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_dest_id.id),
            ]
        if product_ids:
            clause_1 += [('product_id','in',product_ids)]
        if self.account_analytic_dest_id:
            clause_1 += [('account_analytic_dest_id','=', self.account_analytic_dest_id.id)]
        clause_2 = []
        if self.start_date:
            clause_2 = [('date_expected','>=',self.start_date)]
            if self.date_of_transfer:
                clause_2 = [('picking_id.date_done','>=',self.start_date)]
        elif self.end_date:
            clause_2 = [('date_expected','<=',self.end_date)]
            if self.date_of_transfer:
                clause_2 = [('picking_id.date_done','>=',self.end_date)]
        elif self.start_date and self.end_date:
            clause_2 = [('date_expected','>=',self.start_date),('date_expected','<=',self.end_date)]
            if self.date_of_transfer:
                clause_2 = [('picking_id.date_done','>=',self.start_date),('picking_id.date_done','<=',self.end_date)]
        # print "======1=======",clause_1
        # print "======2=======",clause_2
        clause = clause_1+clause_2
        #print "======1=======",clause
        stock_ids = self.env['stock.move'].search(clause, order = 'location_id, location_dest_id, date_expected, account_analytic_dest_id')
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