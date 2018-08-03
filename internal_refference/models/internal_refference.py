# -*- coding: utf-8 -*-
##############################################################################
#      
#    Copyright (C) 2016 Sicepat Ekspres Indonesia (<http://www.sicepat.com>).
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# 1 : imports of python lib


# 2 :  imports of openerp
from openerp import models, fields, api

###LAMA
class templateproduct(models.Model):
    _name = "product.default.code"

    name = fields.Char("Internal Refference",required=True)
    type = fields.Selection([('biaya', 'Biaya'),('asset', 'Asset'),('material', 'Material')],required=True)

###BARU
class producttemplate(models.Model):
    _inherit = "product.template"
    schedule_hari = fields.Integer(string='Schedule Date (N+hari)',default=3)
    duration = fields.Integer(string='Duration')
    
    internal_reff = fields.Many2one('product.default.code','Internal Refference',required=True)

    @api.onchange('internal_reff')  # if these fields are changed, call  method
    def check_change(self):
        if self.internal_reff:
            self.default_code = self.internal_reff.name

class productproduct(models.Model):
    _inherit = "product.product"
    
    internal_reff = fields.Many2one('product.default.code','Internal Refference',required=False)

    @api.onchange('internal_reff')  # if these fields are changed, call  method
    def check_change(self):
        if self.internal_reff:
            self.default_code = self.internal_reff.name

