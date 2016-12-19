# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 STI (<https://github.com/sumihai-tekindo>).
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

from openerp.osv import osv
from openerp.tools.translate import _

class account_invoice_confirm(osv.osv_memory):
    """
    This wizard will confirm the all the selected approve invoices
    """

    _inherit = "account.invoice.confirm"

    def invoice_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []

        proxy = self.pool['account.invoice']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('draft', 'proforma', 'proforma2', 'approved'):
                raise osv.except_osv(_('Warning!'), _("Selected invoice(s) cannot be confirmed as they are not in 'Draft', 'Pro-Forma' or 'Approve' state."))
            record.signal_workflow('invoice_open')
            
        return {'type': 'ir.actions.act_window_close'}


class account_invoice_submit(osv.osv_memory):
    """
    This wizard will submit the all the selected draft invoices
    """

    _name = "account.invoice.submit"
    _description = "Submit the selected invoices"

    def invoice_submit(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []

        if not self.pool['res.users'].has_group(cr, uid, 'invoice_supplier_validate.group_submit_invoices'):
            raise osv.except_osv(_('Warning!'), _("You don't have access to submit the selected invoice(s)."))
        
        proxy = self.pool['account.invoice']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('draft', 'proforma', 'proforma2'):
                raise osv.except_osv(_('Warning!'), _("Selected invoice(s) cannot be submitted as they are not in 'Draft' or 'Pro-Forma' state."))
            record.signal_workflow('invoice_submit')
            
        return {'type': 'ir.actions.act_window_close'}


class account_invoice_acknowledge(osv.osv_memory):
    """
    This wizard will acknowledge the all the selected submit invoices
    """

    _name = "account.invoice.acknowledge"
    _description = "Acknowledge the Selected Invoices"

    def invoice_acknowledge(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        proxy = self.pool['account.invoice']
        active_ids = context.get('active_ids', []) or []

        if not self.pool['res.users'].has_group(cr, uid, 'invoice_supplier_validate.group_acknowledge_invoices'):
            raise osv.except_osv(_('Warning!'), _("You don't have access to acknowledge the selected invoice(s)."))
        
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('submit'):
                raise osv.except_osv(_('Warning!'), _("Selected invoice(s) cannot be acknowledge as they are not in 'Submit' state."))
            record.signal_workflow('invoice_acknowledge')
        return {'type': 'ir.actions.act_window_close'}

class account_invoice_approve(osv.osv_memory):
    """
    This wizard will approve the all the selected submit or acknowledge invoices
    """

    _name = "account.invoice.approve"
    _description = "Approve the Selected Invoices"

    def invoice_approve(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        proxy = self.pool['account.invoice']
        active_ids = context.get('active_ids', []) or []

        if not self.pool['res.users'].has_group(cr, uid, 'invoice_supplier_validate.group_approve_invoices'):
            raise osv.except_osv(_('Warning!'), _("You don't have access to approve the selected invoice(s)."))
        
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('submit', 'acknowledge'):
                raise osv.except_osv(_('Warning!'), _("Selected invoice(s) cannot be approve as they are not in 'Submit' or 'Acknowledge' state."))
            record.signal_workflow('invoice_approve')
        return {'type': 'ir.actions.act_window_close'}

