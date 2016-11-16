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

from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'property_account_advance_payable': fields.property(
            type='many2one',
            relation='account.account',
            string="Account Advance Payable",
            domain="[('type', '=', 'payable')]",
            help="This account will be used instead of the default one as the payable advance account for the current partner",
            required=True),
        'property_account_advance_receivable': fields.property(
            type='many2one',
            relation='account.account',
            string="Account Advance Receivable",
            domain="[('type', '=', 'receivable')]",
            help="This account will be used instead of the default one as the receivable advance account for the current partner",
            required=True),
    }
