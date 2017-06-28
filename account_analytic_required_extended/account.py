# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Pambudi Satria (<https://github.com/pambudisatria>).
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

from openerp import api, models, _
from openerp.exceptions import ValidationError, Warning

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _get_analytic_policy(self, account):
        """ Extension point to obtain analytic policy for an account """
        return account.user_type.analytic_policy

    @api.one
    @api.constrains('analytic_account_id', 'account_id', 'price_subtotal')
    def _check_constraint_analytic_account(self):
        context = dict(self._context or {})
        if context.get('skip_analytic_required'):
            return True
        if self.price_subtotal == 0:
            return True
        analytic_policy = self._get_analytic_policy(self.account_id)
        if analytic_policy == 'always' and not self.account_analytic_id:
            raise Warning(_("Analytic policy is set to 'Always' with account "
                     "%s '%s' but the analytic account is missing in "
                     "the account invoice line with label '%s'.") % \
                    (self.account_id.code,
                     self.account_id.name,
                     self.name))
        elif analytic_policy == 'never' and self.account_analytic_id:
            raise Warning(_("Analytic policy is set to 'Never' with account %s "
                         "'%s' but the account invoice line with label '%s' "
                         "has an analytic account %s '%s'.") % \
                        (self.account_id.code,
                         self.account_id.name,
                         self.name,
                         self.analytic_account_id.code,
                         self.analytic_account_id.name))
        return True
