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

import time
import datetime



class account_duedate(osv.osv):
    _name = "account.invoice.duedate"
    _description = "Due Date"
    _columns = {
        'invoice_date': fields.date('Invoice date', required=True),
    }

    def invoice_confirm(self, cr, uid, ids, context=None):
        acc_obj = self.pool.get('account.invoice')
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []
        obj = self.browse(cr, uid, ids[0], context=context)
        invoice_date = obj.invoice_date;

        for active_id in active_ids :
            domain = [('id', '=', active_id)]
            lines = acc_obj.search(cr,uid, domain)
            for line in acc_obj.browse(cr, uid, lines):
                term = line.partner_id.property_payment_term.note[:-4];
                term = int(term);
                ref = line.number;

                date_1 = datetime.datetime.strptime(invoice_date, "%Y-%m-%d")
                date_due = date_1 + datetime.timedelta(days=term)

                # print 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',active_id,obj.invoice_date,date_invoice,ref;
                if invoice_date :
                    cr.execute("update account_invoice set date_due = %s,date_invoice = %s where id = %s",(date_due,invoice_date,active_id))
                    cr.execute("update account_move_line set date_maturity = %s where ref = %s",(date_due,ref))

        return {'type': 'ir.actions.act_window_close'}


