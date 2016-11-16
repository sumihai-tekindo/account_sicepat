# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Pambudi Satria (<https://github.com/pambudisatria>).
#    @author Pambudi Satria <pambudi.satria@yahoo.com>
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

import datetime
import time

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools.translate import _

class account_invoice_send_mail(osv.osv_memory):
    """
    This wizard will only send Invoice with "Open" status to Customer by Email.
    """

    _name = "account.invoice.send_mail"
    _description = "Send open invoices by Email"

    _columns = {
        'date_invoice': fields.date(string='Invoice Date', help="Date of Invoices will be send by Email"),
    }
    
    _defaults = {
        'date_invoice': lambda *a: time.strftime(DF),
    }

#     def send_invoice_mail(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         invoice = self.pool['account.invoice']
#         mail_template = self.pool['email.template']
#         mod_obj = self.pool['ir.model.data']
# 
#         context.update({
#             'default_model': 'account.invoice',
#             'mark_invoice_as_sent': True
#         }) 
#         template_id = mod_obj.get_object_reference(cr, uid, 'account', 'email_template_edi_invoice')[1]
#         if not template_id:
#             template_id = mail_template.search(cr, uid, [('model', '=', 'account.invoice')], limit=1)
# 
#         date_invoice = self.read(cr, uid, ids, ['date_invoice'], context=context)[0]['date_invoice']
#         domain = [('type','=','out_invoice'), ('date_invoice', '=', date_invoice)]
#         inv_ids = invoice.search(cr, uid, domain)
#         for inv in invoice.browse(cr, uid, inv_ids, context=context):
#             if inv.state == 'open':
#                 if inv.sent:
#                     continue
#                 #send email
#                 context['default_res_id'] = [inv.id] 
#                 mail_template.send_mail(cr, uid, [template_id], inv.id, force_send=True, raise_exception=True, context=context)
#                 
#             
#         return {'type': 'ir.actions.act_window_close'}

    def send_invoice_mail(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        date_invoice = self.read(cr, uid, ids, ['date_invoice'], context=context)[0]['date_invoice']
        domain = [('type','=','out_invoice'), ('date_invoice', '=', date_invoice)]
        inv_ids = self.pool['account.invoice'].search(cr, uid, domain, order='id')
        cron_vals = {
            'name': 'process_after_action',
            'user_id': uid,
            'interval_number': 5,
            'interval_type': 'minutes',
            'numbercall': 1,
            'nextcall': datetime.datetime.utcnow().strftime(DTF),
            'model': 'account.invoice',
            'function': 'action_send_invoice_mail',
            'args': repr([inv_ids]),
            'priority': 5,
        }
        self.pool['ir.cron'].create(cr, uid, cron_vals)
            
        return {'type': 'ir.actions.act_window_close'}

