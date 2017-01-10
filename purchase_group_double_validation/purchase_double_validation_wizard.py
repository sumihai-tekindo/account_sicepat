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

class purchase_order_confirm(osv.osv_memory):
    """
    This wizard will confirm the all the selected purchase order
    """
    
    _name = 'purchase.order.confirm'
    _description = "Confirm the Selected Purchases"

    def purchase_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        proxy = self.pool['purchase.order']
        active_ids = context.get('active_ids', []) or []

        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('draft', 'sent', 'bid'):
                raise osv.except_osv(_('Warning!'), _("Selected order(s) cannot be confirmed as they are not in 'Draft PO', 'RFQ' or 'Bid Received' state."))
            record.signal_workflow('purchase_confirm')
        return {'type': 'ir.actions.act_window_close'}

class purchase_order_approve(osv.osv_memory):
    """
    This wizard will approve the all the selected purchase order
    """
    
    _name = 'purchase.order.approve'
    _description = "Approve the Selected Purchases"

    def purchase_approve(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        proxy = self.pool['purchase.order']
        active_ids = context.get('active_ids', []) or []

        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('confirmed'):
                raise osv.except_osv(_('Warning!'), _("Selected order(s) cannot be approved as they are not in 'Waiting Approval' state."))
            record.signal_workflow('purchase_approve')
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
