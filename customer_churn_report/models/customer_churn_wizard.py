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

from openerp import models, fields, api

class CustomerChurnWizard(models.TransientModel):
    _name = 'customer.churn.wizard'
    
    as_of_date = fields.Date(string='As of Date', default=lambda self: fields.Date.context_today(self), required=True)
    interval_cust_churn_number = fields.Integer(string='Interval Churn Number', default=14)
    interval_cust_churn_type = fields.Selection(selection=[
        ('days', 'Day(s)'),
        ('weeks', 'Week(s)'),
        ('months', 'Month(s)'),
        ], string='Interval Churn Type', default='days', required=True)

    @api.onchange('interval_cust_churn_number')
    def onchange_interval_cust_churn_number(self):
        if self.interval_cust_churn_number <= 0:
            self.interval_cust_churn_number = 14
            self.interval_cust_churn_type = 'days'

    @api.multi
    def _print_report(self, data):
        return {'type': 'ir.actions.report.xml',
                'report_name': 'customer.churn.report.xls',
                'datas': data}

    @api.multi
    def check_report(self):
        context = dict(self._context or {})
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['as_of_date', 'interval_cust_churn_number', 'interval_cust_churn_type'])[0]
        return self._print_report(data)
