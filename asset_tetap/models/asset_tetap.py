from openerp import models, fields, api, _

class asset_tetap(models.TransientModel):
    _name="asset.tetap"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    state = fields.Selection(string="State", selection=[("draft","Draft"),("open","Running"),("all","All")], required=True)
    
        
    @api.multi
    def print_report(self,):
        self.ensure_one()
        state= self.state
        if state=="all":
            state=["draft","open"]
        else:
            state=[self.state] 
        ass_ids = self.env['account.asset.asset'].search([("state","in",state)])
        # ass_ids = self.env['account.asset.asset'].search([])
        list_ass = [ass.id for ass in ass_ids]
        datas={
            'model'    : 'account.asset.asset',
            "ids"    : list_ass,
            'start_date':self.start_date,
            'end_date':self.end_date,
        }
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'report.asset.tetap.xls',
            'datas': datas
        }