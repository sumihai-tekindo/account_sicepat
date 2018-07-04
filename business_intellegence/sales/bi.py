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


class bi_revenue_package_rpt(osv.osv):
    _name = "bi.revenue.package.rpt"
    _description = "BI revenue package report"

    def default_get(self,fields_list):
        res = super(bi_revenue_package_rpt, self).default_get(fields_list)
        return res

    _columns = {
        'date': fields.date(string='Date'),
        'type': fields.char(string='Type'),
        'layanan': fields.char(string='Layanan'),
        'amount': fields.float(string='Amount', digits=(20,0)),
    }

class bi_revenue_location_rpt(osv.osv):
    _name = "bi.revenue.location.rpt"
    _description = "BI revenue by location report"

    def default_get(self,fields_list):
        res = super(bi_revenue_location_rpt, self).default_get(fields_list)
        return res

    _columns = {
        'tag': fields.char(string='tag'),
        'type': fields.char(string='Type'),
        'gerai': fields.char(string='Gerai'),
        'date': fields.date(string='Date'),
        'amount': fields.float(string='Amount', digits=(20,0)),
    }


class bi_revenue_sales_rpt(osv.osv):
    _name = "bi.revenue.sales.rpt"
    _description = "BI revenue by sales report"
    _order_by = "joindate"

    # def _status_customer(self, cr, uid, ids, name, arg, context=None):
    #     res = {}
    #     line_id_obj   =  self.pool.get('account.invoice') 
    #     for linea in self.browse(cr, uid, ids, context=context):
    #         partner_id = linea.partner_id.id;
    #         date_invoice_a = linea.invoice_date;
    #         num = 0;

    #         cr.execute("select date_invoice from account_invoice \
    #         where partner_id = %s order by date_invoice ASC limit 1",(partner_id,))

    #         for row in cr.dictfetchall():

    #             print 'AAAAAAAAAAAAAAAAAAA_date_invoice',row['date_invoice'];
    #             res[linea.id] = True;

    #     return res

    _columns = {
        'invoice_date': fields.date(string='Invoice Date'),
        'gerai': fields.many2one('account.analytic.account', string='Gerai'),
        'user_id': fields.many2one('res.users',string='Sales'),
        'partner_id': fields.many2one('res.partner',string='Customer'),
        'joindate': fields.date(string='Join Date'),
        'package': fields.integer(type='integer',string='#Package Delivered', size=6),
        'weight': fields.float(string='Weight'),
        'gross_amount': fields.float(string='Gross Amount'),
        'disc': fields.float(string='% Discount' ),
        'discount': fields.float(string='Discount'),
        'refund': fields.float(string='Refund'),
        'net_revenue': fields.float(string='Net Revenue'),
        'amount_total': fields.float(string='Net Amount'),
        'tag': fields.related('gerai','tag', type='char',string='Tag', store=True ),
        'state': fields.char(string='State', size=100 ),
        'type': fields.char(string='Type', size=100 ),
        'layanan': fields.char(string='Layanan', size=100 ),
        # 'first_invoice': fields.function(_status_customer, string='First Invoice', type='boolean', store=True),

        'first_invoice': fields.boolean(string='First Invoice'),

   }


class bi_sales_target(osv.osv):
    _name = "bi.sales.target"
    _description = "BI Sales Target"


    _columns = {
        'date': fields.date(string='Date'),
        'package': fields.integer(string='#Package'),
        'net_revenue': fields.float(string='Revenue', digits=(20,2)),
    }


class bi_revenue_pendapatan(osv.osv):
    _name = "bi.revenue.pendapatan"
    _description = "BI Revenue Pendapatan"


    _columns = {
        'code': fields.char(string='Code'),
        'date': fields.date(string='Date'),
        'account': fields.char(string='Account'),
        'jurnal': fields.char(string='Jurnal'),
        'debit': fields.float(string='Debit', digits=(20,2)),
        'credit': fields.float(string='Credit', digits=(20,2)),
        'balance': fields.float(string='Balance', digits=(20,2)),
    }
