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

from openerp.osv import osv, fields

class stock_invoice_onshipping(osv.osv_memory):
    _inherit = "stock.invoice.onshipping"

    _defaults = {
        'invoice_date': fields.date.context_today,
    }


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
        'department_inv_id': fields.many2one('account.invoice.department', 'Department', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, ondelete='set null'),
    }
    
    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        inv_vals = super(stock_picking, self)._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)
        if move.picking_id and move.picking_id.department_id:
            department = move.picking_id.department_id
            inv_vals.update({
                'department_id': department.id,
            })
        return inv_vals

class stock_quant(osv.osv):
    _inherit = 'stock.quant'
    
    def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
        move_lines = super(stock_quant, self)._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
        department_id = move.picking_id and move.picking_id.department_id and move.picking_id.department_id.id or False
        for line in move_lines:
            line[2]['department_id'] = department_id
        return move_lines
