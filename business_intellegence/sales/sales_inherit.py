# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://sicepat.com>).
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

from openerp.osv import fields, osv, expression
from openerp.tools.translate import _




class res_partner_sales3(osv.osv):
    _inherit = "res.partner"
    _description = "res Partner"
    _columns = {
        'rds_code': fields.char(string='RDS Customer Code'),
    }

class account_invoice_line3(osv.osv):
    _inherit = "account.invoice.line"

    def _package_val(self, cr, uid, ids, name, arg, context=None):
        rep = {}
        num = 0;
        for linea in self.browse(cr, uid, ids, context=context):
            num = 1;
            rep[linea.id] = num;

        return rep

    _columns = {
        'date_invoice': fields.related('invoice_id','date_invoice', type='date', string='Date' ),
        'tag': fields.related('account_analytic_id','tag', type='char', string='Tag' ),
        'layanan' : fields.many2one('consignment.service.type', string='Service Type'),
        'package': fields.function(_package_val, string='#Package Delivery', type='integer'),
    }


class account_invoice3(osv.osv):
    _inherit = "account.invoice"


    def _package_count(self, cr, uid, ids, name, arg, context=None):
        line_id_obj   =  self.pool.get('account.invoice.line') 
        rep = {}
        for linea in self.browse(cr, uid, ids, context=context):
            num = 0;
            id = linea.id;
            domain = [('invoice_id','=', id)]
            lines = line_id_obj.search(cr, uid, domain)
            for line in line_id_obj.browse(cr, uid, lines):
                num += 1;
            # print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx_package ',id,num;
 
            rep[linea.id] = num;   
        return rep 

    def _weight_count(self, cr, uid, ids, name, arg, context=None):
        line_id_obj   =  self.pool.get('account.invoice.line') 
        rew = {}
        for linea in self.browse(cr, uid, ids, context=context):
            qty = 0;
            id = linea.id;
            domain = [('invoice_id','=', id)]
            lines = line_id_obj.search(cr, uid, domain)
            for line in line_id_obj.browse(cr, uid, lines):
                qty += line.quantity;
            # print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx_package ',id,qty;
 
            rew[linea.id] = qty;   
        return rew 


    def _discount_count(self, cr, uid, ids, name, arg, context=None):
        line_id_obj   =  self.pool.get('account.invoice.line') 
        red = {}
        for linea in self.browse(cr, uid, ids, context=context):
            name ='';
            val_disc = 0;
            price = 0;
            price_before_disc = 0;
            qty = 0;
            discount = 0;
            total_price = 0;
            total_disc = 0;
            id = linea.id;
            domain = [('invoice_id','=', id)]
            lines = line_id_obj.search(cr, uid, domain)
            for line in line_id_obj.browse(cr, uid, lines):
                name = line.partner_id.name;
                price = line.price_unit;
                qty = line.quantity;
                price_before_disc = int(price) * int(qty);
                discount = line.discount;
                val_disc = (int(price_before_disc) * int(discount))/ 100;
                total_disc += int(val_disc);
                total_price += int(price_before_disc);

                # print 'disc_aw',id,name,price,discount,qty,val_disc;
            # print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx_package ',name,total_price,discount,total_disc;
 
            red[linea.id] = total_disc;   
        return red 

    def _gross_count(self, cr, uid, ids, name, arg, context=None):
        line_id_obj   =  self.pool.get('account.invoice.line') 
        reg = {}
        for linea in self.browse(cr, uid, ids, context=context):
            price_unit = 0;
            qty = 0;
            id = linea.id;
            domain = [('invoice_id','=', id)]
            lines = line_id_obj.search(cr, uid, domain)
            for line in line_id_obj.browse(cr, uid, lines):
                price_unit += int(line.price_unit)*int(line.quantity);
            # print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx_package ',id,qty;
 
            reg[linea.id] = price_unit;   
        return reg 


    def _refund_count(self, cr, uid, ids, name, arg, context=None):
        ref = {}
        for linea in self.browse(cr, uid, ids, context=context):
            type2 = '';
            amount_total = 0;
            type2 = linea.type
            amount_total = linea.amount_total

            if type2 == 'out_refund' :
                ref[linea.id] = amount_total;
            else :
                ref[linea.id] = 0;    

            # print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx_type',type2,amount_total;
 
        return ref

    def _status_customer(self, cr, uid, ids, name, arg, context=None):
        res = {}
        line_id_obj   =  self.pool.get('account.invoice') 
        for linea in self.browse(cr, uid, ids, context=context):
            partner_id = linea.partner_id.id;
            date_invoice_a = linea.date_invoice;
            num = 0;

            domain = [('partner_id','=', partner_id)]
            lines = line_id_obj.search(cr, uid, domain, order="date_invoice ASC",limit= 1)
            for line in line_id_obj.browse(cr, uid, lines):
                num = int(num) + 1;
                date_invoice = line.date_invoice;
                # print 'xxxxxxxxxxxxxxxxxxxxxxxxx',partner_id,date_invoice,date_invoice_a;

            if date_invoice_a == date_invoice :
                res[linea.id] = True;
                # print 'new customer';
            else :
                res[linea.id] = False;                

        return res


    _columns = {
        'joindate': fields.related('partner_id','date', type='date', string='Join Date' ),
        'gerai': fields.related('invoice_line','account_analytic_id', relation='account.analytic.account', type='many2one', string='Gerai' ),
        'package': fields.function(_package_count, string='#Package Delivery', type='integer'),
        'weight': fields.function(_weight_count, string='Weight', type='integer'),                          
        'disc': fields.related('invoice_line','discount', type='float', string='% Discount' ),
        'discount': fields.function(_discount_count, string='Discount', type='float'),
        'gross_amount': fields.function(_gross_count, string='Gross Amount', type='float'),
        'refund': fields.function(_refund_count, string='Refund', type='float'),
        'tag': fields.related('gerai','tag', type='char', string='Tag' ),
        'layanan': fields.related('invoice_line','layanan', relation='consignment.service.type', type='many2one', string='Layanan' ),
        'first_invoice': fields.function(_status_customer, string='First Invoice', type='boolean'),

   }

