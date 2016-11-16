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

from openerp.osv import osv
from openerp.tools.translate import _

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        move_line = super(account_voucher, self).writeoff_move_line_get(cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=context)
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context)
        if (move_line and not voucher.payment_option == 'with_writeoff' and voucher.partner_id):
            if voucher.type in ('sale', 'receipt'):
                account_id = voucher.partner_id.property_account_advance_receivable.id
            else:
                account_id = voucher.partner_id.property_account_advance_payable.id
            if not account_id:
                raise osv.except_osv(_('Missing Configuration on Partner !'),
                    _('Please Fill Advance Accounts on Partner !'))
            move_line['account_id'] = account_id
        return move_line