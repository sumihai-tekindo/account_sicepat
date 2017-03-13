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

import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
import logging
_logger = logging.getLogger(__name__)


class partner_balance(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(partner_balance, self).__init__(cr, uid, name, context=context)

    def set_context(self, objects, data, ids, report_type=None):
        ctx = {}
        query_params = {}
        ctx['state'] = 'posted'
        if data.get('start_date') and data.get('end_date'):
            ctx['date_from'] = data['start_date'] 
            ctx['date_to'] = data['end_date']
        self.ACCOUNT_TYPE = ('receivable',)
        self.display_detail = data.get('display_detail', False)
        self.report_type = data.get('t_report', '')
        self.account_ids = data.get('account_ids', [])
        obj_move = self.pool.get('account.move.line')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        if 'l.account_id' not in self.query and self.account_ids:
            query_params['account_ids'] = tuple(self.account_ids)
            self.query += ' AND l.account_id IN %(account_ids)s'
            self.query = self.cr.mogrify(self.query, query_params)
        lines = self.lines()
        result_with_partner = self.get_result_with_partner(lines)
        result_without_partner = self.get_result_without_partner(lines)
        result_payment_responsible = self._group_payment_responsible(lines)
        self.localcontext.update({
            'lines': lambda: lines,
            'result_with_partner': lambda: result_with_partner,
            'result_without_partner': lambda: result_without_partner,
            'result_payment_responsible': lambda: result_payment_responsible,
        })
        return super(partner_balance, self).set_context(objects, data, ids, report_type=report_type)
    
    def lines(self):
        move_state = ['posted']
        select = from_table = group_by = ""
        order_by = "ORDER BY l.account_id, p.name"
        if self.report_type:
            if self.report_type == 'daily_receivable':
                select = "ap.fiscalyear_id AS fiscal_id, fy.name AS fiscal, l.period_id, ap.code AS period_name, "
                from_table = "JOIN account_period ap ON (l.period_id = ap.id) JOIN account_fiscalyear fy ON (ap.fiscalyear_id=fy.id) "
                group_by = ", ap.fiscalyear_id, fy.name, l.period_id, ap.code "
                order_by = "ORDER BY ap.fiscalyear_id, l.period_id, p.name, l.account_id"
            if self.report_type == 'outstanding_followup':
                select = "p.payment_responsible_id, pu.name AS payment_responsible_name, "
                from_table = "LEFT JOIN res_users u ON (p.payment_responsible_id=u.id) LEFT JOIN res_partner pu ON (u.partner_id=pu.id) "
                group_by = ", p.payment_responsible_id, pu.name "
                order_by = "ORDER BY p.payment_responsible_id, p.name, l.account_id"
        self.cr.execute(
            "SELECT " \
                "p.ref, l.account_id, ac.name AS account_name, ac.code AS code, " \
                "ap.fiscalyear_id AS fiscal_id, fy.name AS fiscal, l.period_id, ap.code AS period_name, " \
                "p.payment_responsible_id, pu.name AS payment_responsible_name, " \
                "p.name, " \
                "sum(l.debit) AS debit, sum(l.credit) AS credit, " \
                    "CASE WHEN sum(l.debit) > sum(l.credit) " \
                        "THEN sum(l.debit) - sum(l.credit) " \
                        "ELSE 0 " \
                    "END AS sdebit, " \
                    "CASE WHEN sum(l.debit) < sum(l.credit) " \
                        "THEN sum(l.credit) - sum(l.debit) " \
                        "ELSE 0 " \
                    "END AS scredit, " \
                "sum(COALESCE(lrf.debit, 0)) AS debit_full, sum(COALESCE(lrf.credit, 0)) AS credit_full, " \
                    "CASE WHEN sum(COALESCE(lrf.debit, 0)) > sum(COALESCE(lrf.credit, 0)) " \
                        "THEN sum(COALESCE(lrf.debit, 0)) - sum(COALESCE(lrf.credit, 0)) " \
                        "ELSE 0 " \
                    "END AS sdebit_full, " \
                    "CASE WHEN sum(COALESCE(lrf.debit, 0)) < sum(COALESCE(lrf.credit, 0)) " \
                        "THEN sum(COALESCE(lrf.credit, 0)) - sum(COALESCE(lrf.debit, 0)) " \
                        "ELSE 0 " \
                    "END AS scredit_full " \
            "FROM account_move_line l " \
            "LEFT OUTER JOIN account_move_line lrf ON (l.reconcile_id=lrf.reconcile_id and l.id<>lrf.id) " \
            "LEFT JOIN res_partner p ON (l.partner_id=p.id) " \
            "JOIN account_period ap ON (l.period_id = ap.id) JOIN account_fiscalyear fy ON (ap.fiscalyear_id=fy.id) " \
            "LEFT JOIN res_users u ON (p.payment_responsible_id=u.id) LEFT JOIN res_partner pu ON (u.partner_id=pu.id) " \
            "JOIN account_account ac ON (l.account_id = ac.id) " \
            "JOIN account_move am ON (am.id = l.move_id) " \
            "WHERE ac.type IN %s " \
            "AND am.state IN %s " \
            "AND " + self.query + "" \
            "GROUP BY p.id, p.ref, p.name, l.account_id, ac.name, ac.code, " \
            "ap.fiscalyear_id, fy.name, l.period_id, ap.code, " \
            "p.payment_responsible_id, pu.name " \
            "" + order_by + "",
            (self.ACCOUNT_TYPE, tuple(move_state)))
        
        return [res for res in self.cr.dictfetchall()]
        
    def get_result_with_partner(self, full_result):
        res = [res for res in full_result if res.get('name')]
        res = self._group_fiscal_period(res)
        periods = {}
        fiscal = [r['fiscal'] for r in res if r['type']==3]
        for f in fiscal:
            periods[f] = {}
            for m in ['00','01','02','03','04','05','06','07','08','09','10','11','12']:
                periods[f][m] = 0.0
        for r in res:
            if r['type'] == 2:
                periods[r['fiscal']][r['period_name']] = r.get('balance', 0.0)
        return (periods, fiscal)

    def get_result_without_partner(self, full_result):
        res = [res for res in full_result if not res.get('name')]
        res = self._group_fiscal_period(res)
        return sum(r['balance'] for r in res if r['type']==3)
        
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
        tot_debit_full = 0.0
        tot_credit_full = 0.0
        tot_sdebit_full = 0.0
        tot_scredit_full = 0.0
        for r in cleanarray:
            # For the first element we always add the line
            # type = 1 is the line is the first of the account
            # type = 2 is an other line of the account
            if i==0:
                # We add the first as the header
                tot_debit = r['debit']
                tot_credit = r['credit_full']
                tot_sdebit =  r['debit'] > r['credit_full'] and r['debit'] - r['credit_full'] or 0.0  
                tot_scredit = r['debit'] < r['credit_full'] and r['credit_full'] - r['debit'] or 0.0
                tot_partner = (r['debit'] or r['credit_full']) and 1 or 0
                tot_debit_full = r['debit_full']
                tot_credit_full = r['credit']
                tot_sdebit_full = r['debit_full'] > r['credit'] and r['debit_full'] - r['credit'] or 0.0
                tot_scredit_full = r['debit_full'] < r['credit'] and r['credit'] - r['debit_full'] or 0.0
                tot_partner_full = (r['debit_full'] or r['credit']) and 1 or 0
                #
                ##
                new_header = {}
                new_header['payment_responsible_name'] = r['payment_responsible_name']
                new_header['payment_responsible_id'] = r['payment_responsible_id']
                new_header['debit'] = tot_debit
                new_header['credit'] = tot_credit
                new_header['sdebit'] = tot_sdebit
                new_header['scredit'] = tot_scredit
                new_header['debit_full'] = tot_debit_full
                new_header['credit_full'] = tot_credit_full
                new_header['sdebit_full'] = tot_sdebit_full
                new_header['scredit_full'] = tot_scredit_full
                new_header['balance'] = float(tot_sdebit) - float(tot_scredit)
                new_header['balance_full'] = float(tot_sdebit_full) - float(tot_scredit_full)
                new_header['partner_count'] = tot_partner
                new_header['partner_count_full'] = tot_partner_full
                new_header['type'] = 3
                ##
                completearray.append(new_header)
                #
                credit = r['credit_full']
                credit_full = r['credit']
                sdebit = r['debit'] > r['credit_full'] and r['debit'] - r['credit_full'] or 0.0
                scredit = r['debit'] < r['credit_full'] and r['credit_full'] - r['debit'] or 0.0 
                sdebit_full = r['debit_full'] > r['credit'] and r['debit_full'] - r['credit'] or 0.0
                scredit_full = r['debit_full'] < r['credit'] and r['credit'] - r['debit_full'] or 0.0 
                r['type'] = 1
                r['credit'] = credit
                r['credit_full'] = credit_full
                r['sdebit'] = sdebit
                r['scredit'] = scredit
                r['sdebit_full'] = sdebit_full
                r['scredit_full'] = scredit_full
                r['balance'] = float(sdebit) - float(scredit)
                r['balance_full'] = float(sdebit_full) - float(scredit_full)

                completearray.append(r)

            else:
                if cleanarray[i]['payment_responsible_id'] <> cleanarray[i-1]['payment_responsible_id']:
                    # we reset the counter
                    tot_debit = r['debit']
                    tot_credit = r['credit_full']
                    tot_sdebit =  r['debit'] > r['credit_full'] and r['debit'] - r['credit_full'] or 0.0  
                    tot_scredit = r['debit'] < r['credit_full'] and r['credit_full'] - r['debit'] or 0.0
                    tot_partner = (r['debit'] or r['credit_full']) and 1 or 0
                    tot_debit_full = r['debit_full']
                    tot_credit_full = r['credit']
                    tot_sdebit_full = r['debit_full'] > r['credit'] and r['debit_full'] - r['credit'] or 0.0
                    tot_scredit_full = r['debit_full'] < r['credit'] and r['credit'] - r['debit_full'] or 0.0
                    tot_partner_full = (r['debit_full'] or r['credit']) and 1 or 0
                    #
                    ##
                    new_header = {}
                    new_header['payment_responsible_name'] = r['payment_responsible_name']
                    new_header['payment_responsible_id'] = r['payment_responsible_id']
                    new_header['debit'] = tot_debit
                    new_header['credit'] = tot_credit
                    new_header['sdebit'] = tot_sdebit
                    new_header['scredit'] = tot_scredit
                    new_header['debit_full'] = tot_debit_full
                    new_header['credit_full'] = tot_credit_full
                    new_header['sdebit_full'] = tot_sdebit_full
                    new_header['scredit_full'] = tot_scredit_full
                    new_header['balance'] = float(tot_sdebit) - float(tot_scredit)
                    new_header['balance_full'] = float(tot_sdebit_full) - float(tot_scredit_full)
                    new_header['partner_count'] = tot_partner
                    new_header['partner_count_full'] = tot_partner_full
                    new_header['type'] = 3
                    ##
                    completearray.append(new_header)
                    #
                    credit = r['credit_full']
                    credit_full = r['credit']
                    sdebit = r['debit'] > r['credit_full'] and r['debit'] - r['credit_full'] or 0.0
                    scredit = r['debit'] < r['credit_full'] and r['credit_full'] - r['debit'] or 0.0 
                    sdebit_full = r['debit_full'] > r['credit'] and r['debit_full'] - r['credit'] or 0.0
                    scredit_full = r['debit_full'] < r['credit'] and r['credit'] - r['debit_full'] or 0.0 
                    r['type'] = 1
                    r['credit'] = credit
                    r['credit_full'] = credit_full
                    r['sdebit'] = sdebit
                    r['scredit'] = scredit
                    r['sdebit_full'] = sdebit_full
                    r['scredit_full'] = scredit_full
                    r['balance'] = float(sdebit) - float(scredit)
                    r['balance_full'] = float(sdebit_full) - float(scredit_full)

                    completearray.append(r)

                if cleanarray[i]['payment_responsible_id'] == cleanarray[i-1]['payment_responsible_id']:

                    tot_debit += r['debit']
                    tot_credit += r['credit_full']
                    tot_sdebit += r['debit'] > r['credit_full'] and r['debit'] - r['credit_full'] or 0.0
                    tot_scredit += r['debit'] < r['credit_full'] and r['credit_full'] - r['debit'] or 0.0
                    tot_partner += (r['debit'] or r['credit_full']) and 1 or 0
                    tot_debit_full += r['debit_full']
                    tot_credit_full += r['credit']
                    tot_sdebit_full += r['debit_full'] > r['credit'] and r['debit_full'] - r['credit'] or 0.0
                    tot_scredit_full += r['debit_full'] < r['credit'] and r['credit'] - r['debit_full'] or 0.0
                    tot_partner_full += (r['debit_full'] or r['credit']) and 1 or 0

                    new_header['debit'] = tot_debit
                    new_header['credit'] = tot_credit
                    new_header['sdebit'] = tot_sdebit
                    new_header['scredit'] = tot_scredit
                    new_header['debit_full'] = tot_debit_full
                    new_header['credit_full'] = tot_credit_full
                    new_header['sdebit_full'] = tot_sdebit_full
                    new_header['scredit_full'] = tot_scredit_full
                    new_header['balance'] = float(tot_sdebit) - float(tot_scredit)
                    new_header['balance_full'] = float(tot_sdebit_full) - float(tot_scredit_full)
                    new_header['partner_count'] = tot_partner
                    new_header['partner_count_full'] = tot_partner_full

                    #
                    credit = r['credit_full']
                    credit_full = r['credit']
                    sdebit = r['debit'] > r['credit_full'] and r['debit'] - r['credit_full'] or 0.0
                    scredit = r['debit'] < r['credit_full'] and r['credit_full'] - r['debit'] or 0.0 
                    sdebit_full = r['debit_full'] > r['credit'] and r['debit_full'] - r['credit'] or 0.0
                    scredit_full = r['debit_full'] < r['credit'] and r['credit'] - r['debit_full'] or 0.0 
                    r['type'] = 1
                    r['credit'] = credit
                    r['credit_full'] = credit_full
                    r['sdebit'] = sdebit
                    r['scredit'] = scredit
                    r['sdebit_full'] = sdebit_full
                    r['scredit_full'] = scredit_full
                    r['balance'] = float(sdebit) - float(scredit)
                    r['balance_full'] = float(sdebit_full) - float(scredit_full)

                    completearray.append(r)

            i = i + 1
        return completearray
