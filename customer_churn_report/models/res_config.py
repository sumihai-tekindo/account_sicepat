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

from openerp import models, fields, api

class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    interval_cust_churn_number = fields.Integer(string='Interval Churn Number', default=14)
    interval_cust_churn_type = fields.Selection(selection=[
        ('days', 'Day(s)'),
        ('weeks', 'Week(s)'),
        ('months', 'Month(s)'),
        ], string='Interval Churn Type', default='days', required=True)

    @api.model
    def get_default_interval_cust_churn_values(self, fields):
        company = self.env.user.company_id
        return {
            'interval_cust_churn_number': company.interval_cust_churn_number,
            'interval_cust_churn_type': company.interval_cust_churn_type,
        }

    @api.one
    def set_interval_cust_churn_values(self):
        company = self.env.user.company_id
        company.interval_cust_churn_number = self.interval_cust_churn_number
        company.interval_cust_churn_type = self.interval_cust_churn_type

    @api.onchange('interval_cust_churn_number')
    def onchange_interval_cust_churn_number(self):
        if self.interval_cust_churn_number <= 0:
            self.interval_cust_churn_number = 14
            self.interval_cust_churn_type = 'days'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
