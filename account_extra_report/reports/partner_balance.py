# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 PT. SUMIHAI TEKNOLOGI INDONESIA. All rights reserved.
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

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.tools.translate import _
from openerp.report import report_sxw

import logging
_logger = logging.getLogger(__name__)

_mapping_periods = {
        '00': _('Opening'),
        '01': _(datetime(1900, int(1), 1).strftime('%B')),
        '02': _(datetime(1900, int(2), 1).strftime('%B')),
        '03': _(datetime(1900, int(3), 1).strftime('%B')),
        '04': _(datetime(1900, int(4), 1).strftime('%B')),
        '05': _(datetime(1900, int(5), 1).strftime('%B')),
        '06': _(datetime(1900, int(6), 1).strftime('%B')),
        '07': _(datetime(1900, int(7), 1).strftime('%B')),
        '08': _(datetime(1900, int(8), 1).strftime('%B')),
        '09': _(datetime(1900, int(9), 1).strftime('%B')),
        '10': _(datetime(1900, int(10), 1).strftime('%B')),
        '11': _(datetime(1900, int(11), 1).strftime('%B')),
        '12': _(datetime(1900, int(12), 1).strftime('%B')),
    }

class partner_balance(report_sxw.rml_parse):

#     def set_context(self, objects, data, ids, report_type=None):
#         ctx = {}
#         query_params = {}
#         ctx['state'] = 'posted'
#         if data.get('start_date') and data.get('end_date'):
#             ctx['date_from'] = data['start_date'] 
#             ctx['date_to'] = data['end_date']
#         res_company = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).company_id
#         self.ACCOUNT_TYPE = ('receivable',)
#         self.display_detail = data.get('display_detail', False)
#         self.report_type = data.get('t_report', '')
#         self.account_ids = data.get('account_ids', [])
#         obj_move = self.pool.get('account.move.line')
#         self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
#         if 'l.account_id' not in self.query and self.account_ids:
#             query_params['account_ids'] = tuple(self.account_ids)
#             self.query += ' AND l.account_id IN %(account_ids)s'
#             self.query = self.cr.mogrify(self.query, query_params)
#         lines = self.lines()
#         result_with_partner = self.get_result_with_partner(lines)
#         result_without_partner = self.get_result_without_partner(lines)
#         daily_receivable_detail = self._group_fiscal_period(lines)
#         result_payment_responsible = self._group_payment_responsible(lines)
#         sum_balance = 0
#         for line in filter(lambda x: x['type'] == 3, daily_receivable_detail):
#             sum_balance += line['balance'] or 0
#         self.localcontext.update({
#             'res_company': res_company,
#             'lines': lambda: lines,
#             'result_with_partner': lambda: result_with_partner,
#             'result_without_partner': lambda: result_without_partner,
#             'daily_receivable_detail': lambda: daily_receivable_detail,
#             'result_payment_responsible': lambda: result_payment_responsible,
#             'sum_balance': lambda: sum_balance,
#         })
#         return super(partner_balance, self).set_context(objects, data, ids, report_type=report_type)
    def set_context(self, objects, data, ids, report_type=None):
        self.result_selection = data.get('result_selection')
        if (self.result_selection == 'customer' ):
            self.ACCOUNT_TYPE = ('receivable',)
        elif (self.result_selection == 'supplier'):
            self.ACCOUNT_TYPE = ('payable',)
        else:
            self.ACCOUNT_TYPE = ('payable', 'receivable')

        self.report_type = data.get('t_report')
        self.start_date = data.get('start_date')
        self.end_date = data.get('end_date')
        self.display_detail = data.get('display_detail')
        self.group_by = data.get('group_by', 'group_fiscal')
        self.account_ids = data.get('account_ids')
        self.target_move = data.get('target_move', 'all')
        lines = self.lines()
        result_with_partner = self.get_result_with_partner(lines)
        result_without_partner = self.get_result_without_partner(lines)
        result_followup = self.get_result_followup(lines)
        result_receivable = self.get_receivable_group_fiscal(lines)
        result_receivable_followup = self.get_receivable_group_followup_fiscal(lines)
        if self.group_by == 'group_partner':
            result_receivable = self.get_receivable_group_partner(lines)
            result_receivable_followup = self.get_receivable_group_followup_partner(lines)
        res_company = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).company_id
        self.localcontext.update({
                'lines': lambda: lines,
                'result_with_partner': lambda: result_with_partner,
                'result_without_partner': lambda: result_without_partner,
                'result_followup': lambda: result_followup,
                'result_receivable': lambda: result_receivable,
                'result_receivable_followup': lambda: result_receivable_followup,
                'res_company': res_company,
            })
        return super(partner_balance, self).set_context(objects, data, ids, report_type=report_type)

    
#     def lines(self):
#         move_state = ['posted']
#         select = from_table = group_by = ""
#         order_by = "ORDER BY l.account_id, p.name"
#         if self.report_type:
#             if self.report_type == 'daily_receivable':
#                 select = "ap.fiscalyear_id AS fiscal_id, fy.name AS fiscal, l.period_id, ap.code AS period_name, "
#                 from_table = "JOIN account_period ap ON (l.period_id = ap.id) JOIN account_fiscalyear fy ON (ap.fiscalyear_id=fy.id) "
#                 group_by = ", ap.fiscalyear_id, fy.name, l.period_id, ap.code "
#                 order_by = "ORDER BY ap.fiscalyear_id, l.period_id, p.name, l.account_id"
#             if self.report_type == 'outstanding_followup':
#                 select = "p.payment_responsible_id, pu.name AS payment_responsible_name, "
#                 from_table = "LEFT JOIN res_users u ON (p.payment_responsible_id=u.id) LEFT JOIN res_partner pu ON (u.partner_id=pu.id) "
#                 group_by = ", p.payment_responsible_id, pu.name "
#                 order_by = "ORDER BY p.payment_responsible_id, p.name, l.account_id"
#         self.cr.execute(
#             "SELECT " \
#                 "p.ref, l.account_id, ac.name AS account_name, ac.code AS code, " \
#                 "ap.fiscalyear_id AS fiscal_id, fy.name AS fiscal, l.period_id, ap.code AS period_name, " \
#                 "p.payment_responsible_id, pu.name AS payment_responsible_name, " \
#                 "p.name, " \
#                 "sum(l.debit) AS debit, sum(l.credit) AS credit, " \
#                     "CASE WHEN sum(l.debit) > sum(l.credit) " \
#                         "THEN sum(l.debit) - sum(l.credit) " \
#                         "ELSE 0 " \
#                     "END AS sdebit, " \
#                     "CASE WHEN sum(l.debit) < sum(l.credit) " \
#                         "THEN sum(l.credit) - sum(l.debit) " \
#                         "ELSE 0 " \
#                     "END AS scredit, " \
#                 "sum(COALESCE(lrf.debit, 0)) AS debit_full, sum(COALESCE(lrf.credit, 0)) AS credit_full, " \
#                     "CASE WHEN sum(COALESCE(lrf.debit, 0)) > sum(COALESCE(lrf.credit, 0)) " \
#                         "THEN sum(COALESCE(lrf.debit, 0)) - sum(COALESCE(lrf.credit, 0)) " \
#                         "ELSE 0 " \
#                     "END AS sdebit_full, " \
#                     "CASE WHEN sum(COALESCE(lrf.debit, 0)) < sum(COALESCE(lrf.credit, 0)) " \
#                         "THEN sum(COALESCE(lrf.credit, 0)) - sum(COALESCE(lrf.debit, 0)) " \
#                         "ELSE 0 " \
#                     "END AS scredit_full, " \
#                 "sum(COALESCE(l.rdebit, 0)) AS rdebit, sum(COALESCE(l.rcredit, 0)) AS rcredit, " \
#                     "CASE WHEN sum(COALESCE(l.rdebit, 0)) > sum(COALESCE(l.rcredit, 0)) " \
#                         "THEN sum(COALESCE(l.rdebit, 0)) - sum(COALESCE(l.rcredit, 0)) " \
#                         "ELSE 0 " \
#                     "END AS srdebit, " \
#                     "CASE WHEN sum(COALESCE(l.rdebit, 0)) < sum(COALESCE(l.rcredit, 0)) " \
#                         "THEN sum(COALESCE(l.rcredit, 0)) - sum(COALESCE(l.rdebit, 0)) " \
#                         "ELSE 0 " \
#                     "END AS srcredit " \
#             "FROM ( " \
#                 "SELECT bal.id, bal.reconcile_id, bal.state, bal.move_id, bal.account_id, bal.period_id, bal.partner_id, bal.debit, bal.credit, red.debit AS rdebit, red.credit AS rcredit " \
#                 "FROM ( " \
#                     "SELECT l.id, l.reconcile_id, l.state, l.move_id, l.account_id, l.period_id, l.partner_id, l.debit, l.credit " \
#                     "FROM account_move_line l " \
#                     "WHERE " + self.query + "" \
#                     ") AS bal " \
#                 "FULL OUTER JOIN ( " \
#                     "SELECT l.id, l.state, l.move_id, l.account_id, l.period_id, l.partner_id, l.debit, l.credit " \
#                     "FROM account_move_line l " \
#                     "WHERE l.date_maturity <= CURRENT_DATE - INTERVAL \'1 months\' " \
#                     "AND l.reconcile_id IS NULL " \
#                     "AND " + self.query + "" \
#                     ") AS red " \
#                     "ON (bal.id=red.id AND bal.move_id=red.move_id AND bal.partner_id=red.partner_id AND bal.account_id=red.account_id AND bal.period_id=red.period_id) " \
#                 ") AS l " \
#             "LEFT OUTER JOIN account_move_line lrf ON (l.reconcile_id=lrf.reconcile_id and l.id<>lrf.id) " \
#             "LEFT JOIN res_partner p ON (l.partner_id=p.id) " \
#             "JOIN account_period ap ON (l.period_id = ap.id) JOIN account_fiscalyear fy ON (ap.fiscalyear_id=fy.id) " \
#             "LEFT JOIN res_users u ON (p.payment_responsible_id=u.id) LEFT JOIN res_partner pu ON (u.partner_id=pu.id) " \
#             "JOIN account_account ac ON (l.account_id = ac.id) " \
#             "JOIN account_move am ON (am.id = l.move_id) " \
#             "WHERE ac.type IN %s " \
#             "AND am.state IN %s " \
#             "AND " + self.query + "" \
#             "GROUP BY p.id, p.ref, p.name, l.account_id, ac.name, ac.code, " \
#             "ap.fiscalyear_id, fy.name, l.period_id, ap.code, " \
#             "p.payment_responsible_id, pu.name " \
#             "" + order_by + "",
#             (self.ACCOUNT_TYPE, tuple(move_state)))
#         
#         return [res for res in self.cr.dictfetchall()]
    def lines(self):
        aml_obj = self.pool.get('account.move.line')
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']

        domain = [
                '&', ('reconcile_id', '=', False), 
                '&', ('account_id.active','=', True), 
                '&', ('account_id.type', '=', 'receivable'), 
                '&', ('state', '!=', 'draft'), 
                ('move_id.state', 'in', tuple(move_state))
            ]
        if self.start_date:
            domain += [('date','>=', self.start_date)]
        if self.end_date:
            domain += [('date', '<=', self.end_date)]
#         if data.get('start_date') and data.get('end_date'):
#             domain += ['&', ('date', '<=', data['end_date']), ('date','>=', data['start_date'])]
        if self.account_ids:
            domain += [('account_id', 'in', tuple(self.account_ids))]

        receivables = []
        lines = aml_obj.search(self.cr, self.uid, domain, order="partner_id ASC, date ASC, account_id ASC")
        for line in aml_obj.browse(self.cr, self.uid, lines):
            receivables.append({
                    'date': line.date,
                    'move_name': line.move_id.name,
                    'date_maturity': line.date_maturity,
                    'fiscal': line.period_id.fiscalyear_id.code,
                    'period_name': line.period_id.code,
                    'account_name': '%s - %s' % (line.account_id.code, line.account_id.name),
                    'payment_responsible_name': line.partner_id and line.partner_id.payment_responsible_id and line.partner_id.payment_responsible_id.name or False,
                    'partner_name': line.partner_id and line.partner_id.name or False,
                    'level': 1,
                    'balance': line.result,
                    'balance_red': (line.date_maturity and line.date_maturity < (datetime.now() + relativedelta(months=-1)).strftime('%Y-%m-%d')) and line.result or 0.0,
                })
        if self.report_type == 'daily_receivable':
            receivables = sorted(receivables, key=lambda k: (k['fiscal'], k['period_name'], k['partner_name'], k['account_name']))
            if self.display_detail and self.group_by == 'group_partner':
                receivables = sorted(receivables, key=lambda k: (k['partner_name'], k['fiscal'], k['period_name'], k['account_name']))
        if self.report_type == 'outstanding_followup':
            receivables = sorted(receivables, key=lambda k: (k['payment_responsible_name'], k['partner_name'], k['fiscal'], k['period_name'], k['account_name']))
            if self.display_detail and self.group_by == 'group_fiscal':
                receivables = sorted(receivables, key=lambda k: (k['payment_responsible_name'], k['fiscal'], k['period_name'], k['partner_name'], k['account_name']))
        return receivables
        
    def get_result_with_partner(self, receivables):
        res = [res for res in receivables if res.get('partner_name')]
        fiscal_periods = {}
        fiscal = set([r['fiscal'] for r in res])
        for f in sorted(fiscal):
            fiscal_periods.setdefault(f, {})
            for p in ['00','01','02','03','04','05','06','07','08','09','10','11','12']:
                fiscal_periods[f][p] = 0.0
        for r in res:
            fiscal_periods[r['fiscal']][r['period_name'].split('/')[0]] += r['balance']
        return (fiscal_periods, fiscal)

    def get_result_without_partner(self, receivables):
        res = [res for res in receivables if not res.get('partner_name')]
        return sum(r['balance'] for r in res)
        
    def get_result_followup(self, receivables):
        res_dict = {}
        i = 0
        for line in receivables:
            key = line['payment_responsible_name'] and line['payment_responsible_name'] or 'Unassigned'
            if res_dict.get(key):
                res_dict[key]['balance'] += line['balance']
                res_dict[key]['balance_red'] += line['balance_red']
                res_dict[key]['partner_count'] += (line['balance'] and receivables[i]['partner_name'] <> receivables[i-1]['partner_name']) and 1 or 0
                res_dict[key]['partner_count_red'] += (line['balance_red'] and receivables[i]['partner_name'] <> receivables[i-1]['partner_name']) and 1 or 0
            else:
                res_dict[key] = {
                        'payment_responsible_name': line['payment_responsible_name'] and line['payment_responsible_name'] or 'Unassigned',
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],                    
                        'partner_count': 1,                    
                        'partner_count_red': line['balance_red'] and 1 or 0,                    
                    }
            i += 1   
        return [v for k, v in res_dict.items()]
        
    def get_receivable_group_fiscal(self, receivables):
        res_dict = {}
        i = 0
        for line in receivables:
            group_fiscal = line['fiscal']
            group_period = line['period_name'].split('/')[0]
            group_partner = line['partner_name'] and line['partner_name'] or 'Unknown Partner'
            group_account = line['account_name'].split('-')[0].strip()
            key_level_account = group_fiscal + '-' + group_period + '-' + group_partner + '-' + group_account
            key_level_partner = group_fiscal + '-' + group_period + '-' + group_partner
            key_level_period = group_fiscal + '-' + group_period
            key_level_fiscal = group_fiscal
            res_dict[key_level_account + '-' + line['date'] + '-' + line['move_name']] = {
                    'date': line['date'],
                    'move_name': line['move_name'],
                    'date_maturity': line['date_maturity'],
                    'level': 4,
                    'balance': line['balance'],
                    'balance_red': line['balance_red'],
                }
            if res_dict.get(key_level_account):
                res_dict[key_level_account]['balance'] += line['balance']
                res_dict[key_level_account]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_account] = {
                        'name': line['account_name'],
                        'level': 3,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_partner):
                res_dict[key_level_partner]['balance'] += line['balance']
                res_dict[key_level_partner]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_partner] = {
                        'name': group_partner,
                        'level': 2,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_period):
                res_dict[key_level_period]['balance'] += line['balance']
                res_dict[key_level_period]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_period] = {
                        'name': _mapping_periods[group_period],
                        'level': 1,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_fiscal):
                res_dict[key_level_fiscal]['balance'] += line['balance']
                res_dict[key_level_fiscal]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_fiscal] = {
                        'name': line['fiscal'],
                        'level': 0,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            i += 1   
        return [v for k, v in sorted(res_dict.items())]
        
    def get_receivable_group_partner(self, receivables):
        res_dict = {}
        i = 0
        for line in receivables:
            group_partner = line['partner_name'] and line['partner_name'] or 'Unknown Partner'
            group_fiscal = line['fiscal']
            group_period = line['period_name'].split('/')[0]
            group_account = line['account_name'].split('-')[0].strip()
            key_level_account = group_partner + '-' + group_fiscal + '-' + group_period + '-' + group_account
            key_level_period = group_partner + '-' + group_fiscal + '-' + group_period
            key_level_fiscal = group_partner + '-' + group_fiscal
            key_level_partner = group_partner
            res_dict[key_level_account + '-' + line['date'] + '-' + line['move_name']] = {
                    'date': line['date'],
                    'move_name': line['move_name'],
                    'date_maturity': line['date_maturity'],
                    'level': 4,
                    'balance': line['balance'],
                    'balance_red': line['balance_red'],
                }
            if res_dict.get(key_level_account):
                res_dict[key_level_account]['balance'] += line['balance']
                res_dict[key_level_account]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_account] = {
                        'name': line['account_name'],
                        'level': 3,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_period):
                res_dict[key_level_period]['balance'] += line['balance']
                res_dict[key_level_period]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_period] = {
                        'name': _mapping_periods[group_period],
                        'level': 2,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_fiscal):
                res_dict[key_level_fiscal]['balance'] += line['balance']
                res_dict[key_level_fiscal]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_fiscal] = {
                        'name': line['fiscal'],
                        'level': 1,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_partner):
                res_dict[key_level_partner]['balance'] += line['balance']
                res_dict[key_level_partner]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_partner] = {
                        'name': group_partner,
                        'level': 0,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            i += 1   
        return [v for k, v in sorted(res_dict.items())]

    def get_receivable_group_followup_fiscal(self, receivables):
        res_dict = {}
        i = 0
        for line in receivables:
            group_payment = line['payment_responsible_name'] and line['payment_responsible_name'] or 'Unassigned'
            group_fiscal = line['fiscal']
            group_period = line['period_name'].split('/')[0]
            group_partner = line['partner_name'] and line['partner_name'] or 'Unknown Partner'
            group_account = line['account_name'].split('-')[0].strip()
            key_level_account = group_payment + '-' + group_fiscal + '-' + group_period + '-' + group_partner + '-' + group_account
            key_level_partner = group_payment + '-' + group_fiscal + '-' + group_period + '-' + group_partner
            key_level_period = group_payment + '-' + group_fiscal + '-' + group_period
            key_level_fiscal = group_payment + '-' + group_fiscal
            key_level_payment = group_payment
            res_dict[key_level_account + '-' + line['date'] + '-' + line['move_name']] = {
                    'date': line['date'],
                    'move_name': line['move_name'],
                    'date_maturity': line['date_maturity'],
                    'level': 5,
                    'balance': line['balance'],
                    'balance_red': line['balance_red'],
                }
            if res_dict.get(key_level_account):
                res_dict[key_level_account]['balance'] += line['balance']
                res_dict[key_level_account]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_account] = {
                        'name': line['account_name'],
                        'level': 4,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_partner):
                res_dict[key_level_partner]['balance'] += line['balance']
                res_dict[key_level_partner]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_partner] = {
                        'name': group_partner,
                        'level': 3,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_period):
                res_dict[key_level_period]['balance'] += line['balance']
                res_dict[key_level_period]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_period] = {
                        'name': _mapping_periods[group_period],
                        'level': 2,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_fiscal):
                res_dict[key_level_fiscal]['balance'] += line['balance']
                res_dict[key_level_fiscal]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_fiscal] = {
                        'name': line['fiscal'],
                        'level': 1,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_payment):
                res_dict[key_level_payment]['balance'] += line['balance']
                res_dict[key_level_payment]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_payment] = {
                        'name': group_payment,
                        'level': 0,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            i += 1   
        return [v for k, v in sorted(res_dict.items())]
        
    def get_receivable_group_followup_partner(self, receivables):
        res_dict = {}
        i = 0
        for line in receivables:
            group_payment = line['payment_responsible_name'] and line['payment_responsible_name'] or 'Unassigned'
            group_partner = line['partner_name'] and line['partner_name'] or 'Unknown Partner'
            group_fiscal = line['fiscal']
            group_period = line['period_name'].split('/')[0]
            group_account = line['account_name'].split('-')[0].strip()
            key_level_account = group_payment + '-' + group_partner + '-' + group_fiscal + '-' + group_period + '-' + group_account
            key_level_period = group_payment + '-' + group_partner + '-' + group_fiscal + '-' + group_period
            key_level_fiscal = group_payment + '-' + group_partner + '-' + group_fiscal
            key_level_partner = group_payment + '-' + group_partner
            key_level_payment = group_payment
            res_dict[key_level_account + '-' + line['date'] + '-' + line['move_name']] = {
                    'date': line['date'],
                    'move_name': line['move_name'],
                    'date_maturity': line['date_maturity'],
                    'level': 5,
                    'balance': line['balance'],
                    'balance_red': line['balance_red'],
                }
            if res_dict.get(key_level_account):
                res_dict[key_level_account]['balance'] += line['balance']
                res_dict[key_level_account]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_account] = {
                        'name': line['account_name'],
                        'level': 4,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_period):
                res_dict[key_level_period]['balance'] += line['balance']
                res_dict[key_level_period]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_period] = {
                        'name': _mapping_periods[group_period],
                        'level': 3,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_fiscal):
                res_dict[key_level_fiscal]['balance'] += line['balance']
                res_dict[key_level_fiscal]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_fiscal] = {
                        'name': line['fiscal'],
                        'level': 2,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_partner):
                res_dict[key_level_partner]['balance'] += line['balance']
                res_dict[key_level_partner]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_partner] = {
                        'name': group_partner,
                        'level': 1,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            if res_dict.get(key_level_payment):
                res_dict[key_level_payment]['balance'] += line['balance']
                res_dict[key_level_payment]['balance_red'] += line['balance_red']
            else:
                res_dict[key_level_payment] = {
                        'name': group_payment,
                        'level': 0,
                        'balance': line['balance'],
                        'balance_red': line['balance_red'],
                    }
            i += 1   
        return [v for k, v in sorted(res_dict.items())]

    def _group_fiscal_period(self, cleanarray):
        i = 0
        completearray = []
        tot_debit_f = 0.0
        tot_credit_f = 0.0
        tot_sdebit_f = 0.0
        tot_scredit_f = 0.0
        tot_debit_full_f = 0.0
        tot_credit_full_f = 0.0
        tot_sdebit_full_f = 0.0
        tot_scredit_full_f = 0.0
        tot_debit_p = 0.0
        tot_credit_p = 0.0
        tot_sdebit_p = 0.0
        tot_scredit_p = 0.0
        tot_debit_full_p = 0.0
        tot_credit_full_p = 0.0
        tot_sdebit_full_p = 0.0
        tot_scredit_full_p = 0.0
        for r in cleanarray:
            # For the first element we always add the line
            # type = 1 is the line is the first of the account
            # type = 2 is an other line of the account
            if i==0:
                # We add the first as the header
                tot_debit_f = r['debit']
                tot_credit_f = r['credit']
                tot_sdebit_f = r['sdebit']
                tot_scredit_f = r['scredit']
                tot_debit_full_f = r['debit_full']
                tot_credit_full_f = r['credit_full']
                tot_sdebit_full_f = r['sdebit_full']
                tot_scredit_full_f = r['scredit_full']
                #
                ##
                new_header_f = {}
                new_header_f['fiscal'] = r['fiscal']
                new_header_f['fiscal_id'] = r['fiscal_id']
                new_header_f['debit'] = tot_debit_f
                new_header_f['credit'] = tot_credit_f
                new_header_f['sdebit'] = tot_sdebit_f
                new_header_f['scredit'] = tot_scredit_f
                new_header_f['debit_full'] = tot_debit_full_f
                new_header_f['credit_full'] = tot_credit_full_f
                new_header_f['sdebit_full'] = tot_sdebit_full_f
                new_header_f['scredit_full'] = tot_scredit_full_f
                new_header_f['balance'] = float(tot_sdebit_f) - float(tot_scredit_f) + float(tot_sdebit_full_f) - float(tot_scredit_full_f)
                new_header_f['type'] = 3
                ##
                completearray.append(new_header_f)
                #
                tot_debit_p = r['debit']
                tot_credit_p = r['credit']
                tot_sdebit_p = r['sdebit']
                tot_scredit_p = r['scredit']
                tot_debit_full_p = r['debit_full']
                tot_credit_full_p = r['credit_full']
                tot_sdebit_full_p = r['sdebit_full']
                tot_scredit_full_p = r['scredit_full']
                #
                ##
                new_header_p = {}
                new_header_p['fiscal'] = r['fiscal']
                new_header_p['fiscal_id'] = r['fiscal_id']
                new_header_p['period_name'] = r['period_name'].split('/')[0]
                new_header_p['period_id'] = r['period_id']
                new_header_p['debit'] = tot_debit_p
                new_header_p['credit'] = tot_credit_p
                new_header_p['sdebit'] = tot_sdebit_p
                new_header_p['scredit'] = tot_scredit_p
                new_header_p['debit_full'] = tot_debit_full_p
                new_header_p['credit_full'] = tot_credit_full_p
                new_header_p['sdebit_full'] = tot_sdebit_full_p
                new_header_p['scredit_full'] = tot_scredit_full_p
                new_header_p['balance'] = float(tot_sdebit_p) - float(tot_scredit_p) + float(tot_sdebit_full_p) - float(tot_scredit_full_p)
                new_header_p['type'] = 2
                ##
                completearray.append(new_header_p)
                #
                r['type'] = 1
                r['balance'] = float(r['sdebit']) - float(r['scredit']) + float(r['sdebit_full']) - float(r['scredit_full'])

                completearray.append(r)

            else:
                if cleanarray[i]['fiscal_id'] <> cleanarray[i-1]['fiscal_id']:
                    # we reset the counter
                    tot_debit_f = r['debit']
                    tot_credit_f = r['credit']
                    tot_sdebit_f = r['sdebit']
                    tot_scredit_f = r['scredit']
                    tot_debit_full_f = r['debit_full']
                    tot_credit_full_f = r['credit_full']
                    tot_sdebit_full_f = r['sdebit_full']
                    tot_scredit_full_f = r['scredit_full']
                    #
                    ##
                    new_header_f = {}
                    new_header_f['fiscal'] = r['fiscal']
                    new_header_f['fiscal_id'] = r['fiscal_id']
                    new_header_f['debit'] = tot_debit_f
                    new_header_f['credit'] = tot_credit_f
                    new_header_f['sdebit'] = tot_sdebit_f
                    new_header_f['scredit'] = tot_scredit_f
                    new_header_f['debit_full'] = tot_debit_full_f
                    new_header_f['credit_full'] = tot_credit_full_f
                    new_header_f['sdebit_full'] = tot_sdebit_full_f
                    new_header_f['scredit_full'] = tot_scredit_full_f
                    new_header_f['balance'] = float(tot_sdebit_f) - float(tot_scredit_f) + float(tot_sdebit_full_f) - float(tot_scredit_full_f)
                    new_header_f['type'] = 3
                    ##
                    completearray.append(new_header_f)
                    #
                    tot_debit_p = r['debit']
                    tot_credit_p = r['credit']
                    tot_sdebit_p = r['sdebit']
                    tot_scredit_p = r['scredit']
                    tot_debit_full_p = r['debit_full']
                    tot_credit_full_p = r['credit_full']
                    tot_sdebit_full_p = r['sdebit_full']
                    tot_scredit_full_p = r['scredit_full']
                    #
                    ##
                    new_header_p = {}
                    new_header_p['fiscal'] = r['fiscal']
                    new_header_p['fiscal_id'] = r['fiscal_id']
                    new_header_p['period_name'] = r['period_name'].split('/')[0]
                    new_header_p['period_id'] = r['period_id']
                    new_header_p['debit'] = tot_debit_p
                    new_header_p['credit'] = tot_credit_p
                    new_header_p['sdebit'] = tot_sdebit_p
                    new_header_p['scredit'] = tot_scredit_p
                    new_header_p['debit_full'] = tot_debit_full_p
                    new_header_p['credit_full'] = tot_credit_full_p
                    new_header_p['sdebit_full'] = tot_sdebit_full_p
                    new_header_p['scredit_full'] = tot_scredit_full_p
                    new_header_p['balance'] = float(tot_sdebit_p) - float(tot_scredit_p) + float(tot_sdebit_full_p) - float(tot_scredit_full_p)
                    new_header_p['type'] = 2
                    ##
                    completearray.append(new_header_p)
                    #
                    r['type'] = 1
                    r['balance'] = float(r['sdebit']) - float(r['scredit']) + float(r['sdebit_full']) - float(r['scredit_full'])

                    completearray.append(r)

                if cleanarray[i]['fiscal_id'] == cleanarray[i-1]['fiscal_id']:
                    tot_debit_f += r['debit']
                    tot_credit_f += r['credit']
                    tot_sdebit_f += r['sdebit']
                    tot_scredit_f += r['scredit']
                    tot_debit_full_f += r['debit_full']
                    tot_credit_full_f += r['credit_full']
                    tot_sdebit_full_f += r['sdebit_full']
                    tot_scredit_full_f += r['scredit_full']

                    new_header_f['debit'] = tot_debit_f
                    new_header_f['credit'] = tot_credit_f
                    new_header_f['sdebit'] = tot_sdebit_f
                    new_header_f['scredit'] = tot_scredit_f
                    new_header_f['debit_full'] = tot_debit_full_f
                    new_header_f['credit_full'] = tot_credit_full_f
                    new_header_f['sdebit_full'] = tot_sdebit_full_f
                    new_header_f['scredit_full'] = tot_scredit_full_f
                    new_header_f['balance'] = float(tot_sdebit_f) - float(tot_scredit_f) + float(tot_sdebit_full_f) - float(tot_scredit_full_f)

                    if cleanarray[i]['period_id'] <> cleanarray[i-1]['period_id']:
                        # we reset the counter
                        tot_debit_p = r['debit']
                        tot_credit_p = r['credit']
                        tot_sdebit_p = r['sdebit']
                        tot_scredit_p = r['scredit']
                        tot_debit_full_p = r['debit_full']
                        tot_credit_full_p = r['credit_full']
                        tot_sdebit_full_p = r['sdebit_full']
                        tot_scredit_full_p = r['scredit_full']
                        #
                        ##
                        new_header_p = {}
                        new_header_p['fiscal'] = r['fiscal']
                        new_header_p['fiscal_id'] = r['fiscal_id']
                        new_header_p['period_name'] = r['period_name'].split('/')[0]
                        new_header_p['period_id'] = r['period_id']
                        new_header_p['debit'] = tot_debit_p
                        new_header_p['credit'] = tot_credit_p
                        new_header_p['sdebit'] = tot_sdebit_p
                        new_header_p['scredit'] = tot_scredit_p
                        new_header_p['debit_full'] = tot_debit_full_p
                        new_header_p['credit_full'] = tot_credit_full_p
                        new_header_p['sdebit_full'] = tot_sdebit_full_p
                        new_header_p['scredit_full'] = tot_scredit_full_p
                        new_header_p['balance'] = float(tot_sdebit_p) - float(tot_scredit_p) + float(tot_sdebit_full_p) - float(tot_scredit_full_p)
                        new_header_p['type'] = 2
                        ##
                        completearray.append(new_header_p)
                   
                    if cleanarray[i]['period_id'] == cleanarray[i-1]['period_id']:
                        tot_debit_p += r['debit']
                        tot_credit_p += r['credit']
                        tot_sdebit_p += r['sdebit']
                        tot_scredit_p += r['scredit']
                        tot_debit_full_p += r['debit_full']
                        tot_credit_full_p += r['credit_full']
                        tot_sdebit_full_p += r['sdebit_full']
                        tot_scredit_full_p += r['scredit_full']
    
                        new_header_p['debit'] = tot_debit_p
                        new_header_p['credit'] = tot_credit_p
                        new_header_p['sdebit'] = tot_sdebit_p
                        new_header_p['scredit'] = tot_scredit_p
                        new_header_p['debit_full'] = tot_debit_full_p
                        new_header_p['credit_full'] = tot_credit_full_p
                        new_header_p['sdebit_full'] = tot_sdebit_full_p
                        new_header_p['scredit_full'] = tot_scredit_full_p
                        new_header_p['balance'] = float(tot_sdebit_p) - float(tot_scredit_p) + float(tot_sdebit_full_p) - float(tot_scredit_full_p)
                        
                    #
                    r['type'] = 1
                    r['balance'] = float(r['sdebit']) - float(r['scredit']) + float(r['sdebit_full']) - float(r['scredit_full'])

                    completearray.append(r)

            i = i + 1
        return completearray

    def _group_payment_responsible(self, cleanarray):
        i = 0
        completearray = []
        tot_debit = 0.0
        tot_credit = 0.0
        tot_sdebit = 0.0
        tot_scredit = 0.0
        tot_debit_red = 0.0
        tot_credit_red = 0.0
        tot_sdebit_red = 0.0
        tot_scredit_red = 0.0
        for r in cleanarray:
            # For the first element we always add the line
            # type = 1 is the line is the first of the account
            # type = 2 is an other line of the account
            if i==0:
                # We add the first as the header
                tot_debit = r['debit']
                tot_credit = r['credit']
                tot_sdebit =  r['sdebit']  
                tot_scredit = r['scredit']
                tot_partner = 1
                tot_debit_red = r['rdebit']
                tot_credit_red = r['rcredit']
                tot_sdebit_red = r['srdebit']
                tot_scredit_red = r['srcredit']
                tot_partner_red = 1
                #
                ##
                new_header = {}
                new_header['payment_responsible_name'] = r['payment_responsible_name']
                new_header['payment_responsible_id'] = r['payment_responsible_id']
                new_header['debit'] = tot_debit
                new_header['credit'] = tot_credit
                new_header['sdebit'] = tot_sdebit
                new_header['scredit'] = tot_scredit
                new_header['rdebit'] = tot_debit_red
                new_header['rcredit'] = tot_credit_red
                new_header['srdebit'] = tot_sdebit_red
                new_header['srcredit'] = tot_scredit_red
                new_header['balance'] = float(tot_sdebit) - float(tot_scredit)
                new_header['balance_full'] = float(tot_sdebit_red) - float(tot_scredit_red)
                new_header['partner_count'] = tot_partner
                new_header['partner_count_red'] = tot_partner_red
                new_header['type'] = 3
                ##
                completearray.append(new_header)
                #
                r['type'] = 1
                r['balance'] = float(r['sdebit']) - float(r['scredit'])
                r['balance_red'] = float(r['srdebit']) - float(r['srcredit'])

                completearray.append(r)

            else:
                if cleanarray[i]['payment_responsible_id'] <> cleanarray[i-1]['payment_responsible_id']:
                    # we reset the counter
                    tot_debit = r['debit']
                    tot_credit = r['credit']
                    tot_sdebit =  r['sdebit']  
                    tot_scredit = r['scredit']
                    tot_partner = 1
                    tot_debit_red = r['rdebit']
                    tot_credit_red = r['rcredit']
                    tot_sdebit_red = r['srdebit']
                    tot_scredit_red = r['srcredit']
                    tot_partner_red = 1
                    #
                    ##
                    new_header = {}
                    new_header['payment_responsible_name'] = r['payment_responsible_name']
                    new_header['payment_responsible_id'] = r['payment_responsible_id']
                    new_header['debit'] = tot_debit
                    new_header['credit'] = tot_credit
                    new_header['sdebit'] = tot_sdebit
                    new_header['scredit'] = tot_scredit
                    new_header['rdebit'] = tot_debit_red
                    new_header['rcredit'] = tot_credit_red
                    new_header['srdebit'] = tot_sdebit_red
                    new_header['srcredit'] = tot_scredit_red
                    new_header['balance'] = float(tot_sdebit) - float(tot_scredit)
                    new_header['balance_red'] = float(tot_sdebit_red) - float(tot_scredit_red)
                    new_header['partner_count'] = tot_partner
                    new_header['partner_count_red'] = tot_partner_red
                    new_header['type'] = 3
                    ##
                    completearray.append(new_header)
                    #
                    r['type'] = 1
                    r['balance'] = float(r['sdebit']) - float(r['scredit'])
                    r['balance_full'] = float(r['srdebit']) - float(r['srcredit'])

                    completearray.append(r)

                if cleanarray[i]['payment_responsible_id'] == cleanarray[i-1]['payment_responsible_id']:

                    tot_debit += r['debit']
                    tot_credit += r['credit']
                    tot_sdebit += r['sdebit']
                    tot_scredit += r['scredit']
                    tot_partner += ((r['debit'] or r['credit']) and cleanarray[i]['name'] <> cleanarray[i-1]['name']) and 1 or 0
                    tot_debit_red += r['rdebit']
                    tot_credit_red += r['rcredit']
                    tot_sdebit_red += r['srdebit']
                    tot_scredit_red += r['srcredit']
                    tot_partner_red += ((r['rdebit'] or r['rcredit']) and cleanarray[i]['name'] <> cleanarray[i-1]['name'])  and 1 or 0

                    new_header['debit'] = tot_debit
                    new_header['credit'] = tot_credit
                    new_header['sdebit'] = tot_sdebit
                    new_header['scredit'] = tot_scredit
                    new_header['rdebit'] = tot_debit_red
                    new_header['rcredit'] = tot_credit_red
                    new_header['srdebit'] = tot_sdebit_red
                    new_header['srcredit'] = tot_scredit_red
                    new_header['balance'] = float(tot_sdebit) - float(tot_scredit)
                    new_header['balance_red'] = float(tot_sdebit_red) - float(tot_scredit_red)
                    new_header['partner_count'] = tot_partner
                    new_header['partner_count_red'] = tot_partner_red

                    #
                    r['type'] = 1
                    r['balance'] = float(r['sdebit']) - float(r['scredit'])
                    r['balance_red'] = float(r['srdebit']) - float(r['srcredit'])

                    completearray.append(r)

            i = i + 1
        return completearray
