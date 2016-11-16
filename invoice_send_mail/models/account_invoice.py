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

from openerp import fields, models, api
from openerp.tools.translate import _

class account_invoice(models.Model):
    # Private attributes
    _inherit = "account.invoice"

    def action_send_invoice_mail(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        if not ids:
            filters = [('type', '=', 'out_invoice'), ('state', '=', 'open'), ('sent', '=', False)]
            ids = self.search(cr, uid, filters, context=context, order='id')
            if not ids:
                return
        mail_template = self.pool['email.template']
        mod_obj = self.pool['ir.model.data']
        template_id = mod_obj.get_object_reference(cr, uid, 'account', 'email_template_edi_invoice')[1]
        if not template_id:
            template_id = mail_template.search(cr, uid, [('model', '=', 'account.invoice')], limit=1)
        ctx = dict(context)
        ctx['default_model'] = 'account.invoice'
        ctx['mark_invoice_as_sent'] = True
        for inv in self.browse(cr, uid, ids):
            if inv.state == 'open':
                if inv.sent:
                    continue
                #send email
                ctx['default_res_id'] = [inv.id]
                mail_template.send_mail(cr, uid, [template_id], inv.id, force_send=True, raise_exception=True, context=ctx)
        return True
