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

from openerp import api
from openerp.osv import osv
from openerp.tools.translate import _

class email_template(osv.osv):
    _inherit = "email.template"

    @api.cr_uid_id_context
    def send_mail(self, cr, uid, template_id, res_id, force_send=False, raise_exception=False, context=None):
        if context is None:
            context = {}
        invoice = self.pool['account.invoice']
        if context.get('default_model') == 'account.invoice' and \
                context.get('default_res_id') and context.get('mark_invoice_as_sent'):
            context['mail_post_autofollow'] = True
            invoice.write(cr, uid, context['default_res_id'], {'sent': True}, context=context)
            invoice.message_post(cr, uid, context['default_res_id'], body=_("Invoice sent"), context=context)
        return super(email_template, self).send_mail(cr, uid, template_id, res_id,  
                force_send=force_send, raise_exception=raise_exception, context=context)


