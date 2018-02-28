from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from openerp.addons.base.ir.ir_cron import _intervalTypes

class goods_request(models.Model):
    _name = "goods.request"
    
    @api.model
    def _get_default_loc(self,):
        loc = 'undefined'
        if self.env.user:
            loc = self.env.user.loc
        return loc

    @api.model
    def is_cabang(self,):
        if self.env.user:
            loc = self.env.user.loc
        print "==============",loc =='cabang' and True or False
        return loc =='cabang' and True or False

    @api.model
    def is_pusat(self,):
        if self.env.user:
            loc = self.env.user.loc
        print "xxxxxxxxxxxxxx",loc =='pusat' and True or False
        return loc =='pusat' and True or False

    name = fields.Char(string="Number")
    user = fields.Many2one('res.users',string="User", default=lambda self: self.env.user, readonly=True)
    
    tgl_req = fields.Datetime(string="Tanggal Request", default=lambda self: fields.Datetime.now(), readonly=True)
    deadline = fields.Date(string='Deadline')
    cabang = fields.Many2one('account.analytic.account', string='Cabang', compute='_compute_cabang')
    goods_request_ids =fields.One2many('goods.request.line','goods_request_id',string='Goods Request')
    state = fields.Selection([
            ('draft','Draft'),
            ('confirmed','Confirmed'),
            ('rejected','Rejected'),
        ], string='Status', default='draft')

    loc = fields.Selection([
            ('cabang','Cabang'),
            ('pusat','Pusat'),
            ('undefined','Undefined'),
        ], string='Location User', default=_get_default_loc)
    is_cabang = fields.Boolean("Is Cabang",default=is_cabang)
    is_pusat = fields.Boolean("Is Pusat",default=is_pusat)

    @api.one
    @api.depends('user')
    def _compute_cabang(self):
        employee = self.env['res.users'].search([('id','=',self.user.id)])
        self.cabang = employee.location.id
        
    
    @api.multi
    def action_confirmed(self):
        self.name = self.env['ir.sequence'].get("GR")
        self.state = 'confirmed'
        
    @api.multi
    def action_rejected(self):
        self.state = 'rejected'

class goods_request_line(models.Model):
    _name = "goods.request.line"

    goods_request_id = fields.Many2one('goods.request')
    product_id = fields.Many2one('product.product', string="Product")
    qty_available = fields.Float(compute='_stock', string="Availibility")
    qty = fields.Float(string='Quantity')
    qty_app = fields.Float(string='Quantity Approve')
    uom = fields.Many2one('product.uom',compute='_uom', string='UOM')

    @api.one
    @api.depends('product_id')
    def _stock(self):
        self.qty_available = self.product_id.qty_available

    @api.one
    @api.depends('product_id')
    def _uom(self):
        self.uom = self.product_id.uom_id.id
    # @api.one
    # @api.depends('user')
    # def _compute_product(self):
    #     user = self.env['hr.employee'].search([('id','=',self.nama_karyawan.id)])
    #     self.product_id = user.product_id.id

class inherit_product_template(models.Model):
    _inherit='product.template'

    cabang = fields.Boolean(string='Cabang')
    pusat = fields.Boolean(string='Pusat')

class product_product(models.Model):
    _inherit='product.product'

    cabang = fields.Boolean(string='Cabang')
    pusat = fields.Boolean(string='Pusat')

class location_inherit(models.Model):
    _inherit='res.users'

    loc = fields.Selection([
            ('cabang','Cabang'),
            ('pusat','Pusat'),
            ('undefined','Undefined'),
        ], string='Location User', default='undefined')

    location = fields.Many2one('account.analytic.account',string = 'Lokasi Pasti')