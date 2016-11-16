# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Sicepat Ekspres (<http://www.sicepat.com>).
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

class wizard_multi_charts_accounts(osv.osv_memory):
    _inherit = 'wizard.multi.charts.accounts'

    def _create_bank_journals_from_o2m(self, cr, uid, obj_wizard, company_id, acc_template_ref, context=None):
        return True

class res_partner_bank(osv.osv):
    _inherit = 'res.partner.bank'
    
    def create(self, cr, uid, vals, context=None):
        res_partner = {}
        res_bank = {}
        if 'partner_id' in vals or vals['partner_id']:
            res_partner = self.onchange_partner_id(cr, uid, [], vals['partner_id'], context)
            if 'owner_name' not in vals or not vals['owner_name']:
                vals['owner_name'] = res_partner['value']['owner_name']
            if 'street' not in vals or not vals['street']:
                vals['street'] = res_partner['value']['street']
            if 'city' not in vals or not vals['city']:
                vals['city'] = res_partner['value']['city']
            if 'zip' not in vals or not vals['zip']:
                vals['zip'] = res_partner['value']['zip']
            if 'country_id' not in vals or not vals['country_id']:
                vals['country_id'] = res_partner['value']['country_id']
            if 'state_id' not in vals or not vals['state_id']:
                vals['state_id'] = res_partner['value']['state_id']
        if 'bank' in vals or vals['bank']:
            res_bank = self.onchange_bank_id(cr, uid, [], vals['bank'], context)
            if 'bank_name' not in vals or not vals['bank_name']:
                vals['bank_name'] = res_bank['value']['bank_name']
            if 'bank_bic' not in vals or not vals['bank_bic']:
                vals['bank_bic'] = res_bank['value']['bank_bic']
        return super(res_partner_bank, self).create(cr, uid, vals, context)
