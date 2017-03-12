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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import AccessError, Warning
# from openerp.osv import fields, osv

# class account_move_line(models.Model):
#     _inherit = "account.move.line"
# 
#     @api.model
#     def _query_get(self, obj='l'):
#         print('context = %s' % dict(self._context or {}))
#         res = super(account_move_line, self)._query_get(obj=obj)
#         print('res = %s' % res)
#         return res

class SiCepatPLAnalysis(models.TransientModel):
    _name = "sicepat.pl.analysis"
    _inherit = "account.common.report"
    _description = "Analisa Rugi Laba SiCepat Ekspres Indonesia"
    
    @api.model
    def _get_to_period(self):
        domain = [
            ('fiscalyear_id', '=', self._get_fiscalyear()),
            ('date_start', '<=', time.strftime('%Y-%m-%d')),
            ('special', '=', False)
        ]
        return self.env['account.period'].search(domain, order='date_stop desc', limit=1)

    @api.model
    def _get_to_date(self):
        period = self._get_to_period()
        return period and (period.date_stop < time.strftime('%Y-%m-%d') and period.date_stop) or time.strftime('%Y-%m-%d')

    date_from = fields.Date(string="Start Date", compute='_get_from_period', readonly=True)
    date_to = fields.Date(default=_get_to_date)
    period_from = fields.Many2one(comodel_name='account.period', string='Start Period', compute='_get_from_period', readonly=True)
    period_to = fields.Many2one(comodel_name='account.period', default=_get_to_period)
    account_report_id = fields.Many2one(comodel_name='account.financial.report', string='Account Reports', required=True)

    @api.one
    @api.depends('fiscalyear_id')
    def _get_from_period(self):
        domain = [
            ('fiscalyear_id', '=', self.fiscalyear_id.id),
            ('special', '=', False)
        ]
        period = self.env['account.period'].search(domain, order='date_start asc, special asc', limit=1)
        if period:
            self.date_from = period.date_start
            self.period_from = period.id

    @api.one
    @api.constrains('date_from', 'date_to')
    def _check_date_to(self):
        if (self.date_from and self.date_to) and self.date_to < self.date_from:
            raise Warning(_('End Date must be greater or equal than Start Date.'))
        date_to = max([p.date_stop for p in self.fiscalyear_id.period_ids])
        if self.date_to > date_to:
            raise Warning(_('Start Date and End Date must be in range between the Fiscal Year.'))
        return True

    @api.onchange('filter', 'fiscalyear_id')
    def onchange_filter(self):
        self.date_to = self.date_from
        self.period_to = self.period_from.id
        domain = [
            ('fiscalyear_id', '=', self.fiscalyear_id.id),
            ('date_start', '<=', time.strftime('%Y-%m-%d')),
            ('special', '=', False)
        ]
        period = self.env['account.period'].search(domain, order='date_stop desc', limit=1)
        if period:
            self.date_to = period.date_stop < time.strftime('%Y-%m-%d') and period.date_stop or time.strftime('%Y-%m-%d')
            self.period_to = period.id

    @api.onchange('date_to', 'period_to')
    def onchange_period_to(self):
        if self.filter == 'filter_period':
            self.date_to = self.env['account.period'].search([('id', '=', self.period_to.id)], limit=1).date_stop
        if self.filter == 'filter_date':
            domain = [
                ('fiscalyear_id', '=', self.fiscalyear_id.id),
                ('date_start', '<=', self.date_to),
                ('special', '=', False)
            ]
            self.period_to = self.env['account.period'].search(domain, order='date_stop desc', limit=1).id
        
    @api.multi
    def _pre_print_report(self, data):
        res = {}
        if not data['form']['fiscalyear_id']:
            raise Warning(_('You must set a fiscal year.'))
        if not data['form']['date_from'] or not data['form']['period_from']:
            raise Warning(_('You must set a start date / period.'))
        if not data['form']['date_to'] or not data['form']['period_to']:
            raise Warning(_('You must set a end date / period.'))
        
        filter = data.get('form') and data['form'].get('filter', False)
        domain = [
            ('fiscalyear_id', '=', data['form']['fiscalyear_id']),
            ('special', '=', False),
            ('date_start', '<=', data['form']['date_to']),
        ]
        periods = self.env['account.period'].search(domain)
        p = [p for p in range(len(periods))]
        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        for i in range(12):
            res[str(i)] = {
                'name': datetime(1900, int(i+1), 1).strftime('%B'),
                'date_from': False,
                'date_to': False,
            }
            stop = start + relativedelta(months=1, days=-1)
            if stop.strftime('%Y-%m-%d') > data['form']['date_to']:
                stop = datetime.strptime(data['form']['date_to'], "%Y-%m-%d")
            if i in p:
                res[str(i)]['date_from'] = start.strftime('%Y-%m-%d')
                res[str(i)]['date_to'] = stop.strftime('%Y-%m-%d')
            start = start + relativedelta(months=1)
        data['form'].update(res)
        data['form'].update(self.read(['account_report_id'])[0])
        data['form']['used_context'].update(self.read(['account_report_id'])[0])
        return data

    @api.multi
    def _print_report(self, data):
        data = self._pre_print_report(data)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.sicepat_pl_analysis_xls',
            'datas': data,
        }