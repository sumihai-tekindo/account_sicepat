from openerp import fields, models, api

class Ticket(models.Model):
    _inherit = 'res.partner'
    
    npwp_number = fields.Char(string='Nomer NPWP', size=15)