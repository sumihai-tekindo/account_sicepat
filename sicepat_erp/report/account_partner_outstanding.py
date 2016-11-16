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

import logging
import time

from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header

_logger = logging.getLogger(__name__)

class partner_outstanding(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(partner_outstanding, self).__init__(cr, uid, name, context=context)
        self.account_ids = []
        self.localcontext.update( {
            'time': time,
            'get_fiscalyear': self._get_fiscalyear,
            'get_journal': self._get_journal,
            'get_filter': self._get_filter,
            'get_account': self._get_account,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_asof_date':self._get_asof_date,
            'get_partners':self._get_partners,
            'get_target_move': self._get_target_move,
        })

    def set_context(self, objects, data, ids, report_type=None):
        self.display_partner = data['form'].get('display_partner', 'non-zero_balance')
        self.result_selection = data['form'].get('result_selection')
        self.filter = data['form'].get('filter', 'filter_no')
        self.target_move = data['form'].get('target_move', 'all')
        self.partner_ids = data['form'].get('partner_ids')
        self.date_as_of = data['form'].get('date_as_of', "(now() at time zone 'UTC')")
        self.show_only_date = data['form'].get('show_only_date')

        if (self.result_selection == 'customer'):
            self.ACCOUNT_TYPE = ('receivable',)
        elif (self.result_selection == 'supplier'):
            self.ACCOUNT_TYPE = ('payable',)
        else:
            self.ACCOUNT_TYPE = ('payable', 'receivable')

        if (self.filter == 'filter_no'):
            self.as_of_date = "(now() at time zone 'UTC')"
        else:
            self.as_of_date = "'%s'" % self.date_as_of
            
        if self.show_only_date:
            self.date_operator = "="
        else:
            self.date_operator = "<="
        
        if self.partner_ids:
            self.where_partner = """inv.partner_id IN """ + str(tuple(self.partner_ids)) + """ AND"""
        else:
            self.where_partner = """inv.partner_id is not null AND"""
        
        res = super(partner_outstanding, self).set_context(objects, data, ids, report_type=report_type)
        lines = self.lines()
        self.localcontext.update({
            'lines': lambda: lines,
        })
        return res

    def lines(self):
        move_state = ['draft','valid']
        if self.target_move == 'posted':
            move_state = ['valid']

        full_account = []
        self.cr.execute(
            """SELECT
                inv.id, inv.partner_id, partner.name, inv.date_invoice, inv.number, inv.amount_total,
                (CASE
                    WHEN move_line.reconcile_id is not null THEN reconcile.balance
                    WHEN move_line.reconcile_partial_id is not null THEN reconcile_partial.balance
                    ELSE inv.amount_total
                END) as balance
            FROM
                account_invoice inv
            LEFT JOIN res_partner partner 
                ON inv.partner_id=partner.id
            JOIN account_account account
                ON inv.account_id=account.id
            LEFT JOIN account_move_line move_line
                ON inv.move_id=move_line.move_id
            LEFT OUTER JOIN (
                SELECT
                    reconcile_id, sum(debit - credit) as balance
                FROM
                    account_move_line
                WHERE
                    reconcile_id is not null AND state IN %s AND date <= """ + self.as_of_date + """
                GROUP BY reconcile_id
                ) reconcile
                ON move_line.reconcile_id=reconcile.reconcile_id
            LEFT OUTER JOIN (
                SELECT
                    reconcile_partial_id, sum(debit - credit) as balance
                FROM
                    account_move_line
                WHERE
                    reconcile_partial_id is not null AND state IN %s AND date <= """ + self.as_of_date + """
                GROUP BY reconcile_partial_id
                ) reconcile_partial
                ON move_line.reconcile_partial_id=reconcile_partial.reconcile_partial_id
            WHERE
                inv.account_id=move_line.account_id AND
                """ + self.where_partner + """
                account.type IN %s AND
                move_line.state IN %s AND
                inv.date_invoice """ + self.date_operator + """ """ + self.as_of_date + """
            ORDER BY partner.name, inv.number""", (
                tuple(move_state),
                tuple(move_state),
                self.ACCOUNT_TYPE, tuple(move_state)
            )
        )
        res = self.cr.dictfetchall()


        if self.display_partner == 'non-zero_balance':
            full_account = [r for r in res if r['balance'] > 0]
        else:
            full_account = [r for r in res]

        for rec in full_account:
            if not rec.get('name', False):
                rec.update({'name': _('Unknown Partner')})

        ## We will now compute Total
        subtotal_row = self._add_subtotal(full_account)
        return subtotal_row

    def _add_subtotal(self, cleanarray):
        i = 0
        completearray = []
        tot_invoice = 0.0
        tot_balance = 0.0
        for r in cleanarray:
            # For the first element we always add the line
            # type = 1 is the line is the first of the partner
            # type = 2 is an other line of the account
            if i==0:
                # We add the first as the header
                #
                ##
                new_header = {}
                new_header['name'] = r['name']
                new_header['number'] = ''
                new_header['amount_total'] = r['amount_total']
                new_header['balance'] = r['balance']
                new_header['type'] = 3
                ##
                completearray.append(new_header)
                #
                r['type'] = 1
                r['name'] = r['date_invoice']

                completearray.append(r)
                #
                tot_invoice = r['amount_total']
                tot_balance = r['balance']
                #
            else:
                if cleanarray[i]['partner_id'] <> cleanarray[i-1]['partner_id']:

                    new_header['amount_total'] = tot_invoice
                    new_header['balance'] = tot_balance
                    new_header['type'] = 3
                    # we reset the counter
                    tot_invoice = r['amount_total']
                    tot_balance = r['balance']
                    #
                    ##
                    new_header = {}
                    new_header['name'] = r['name']
                    new_header['number'] = ''
                    new_header['amount_total'] = tot_invoice
                    new_header['balance'] = tot_balance
                    new_header['type'] = 3
                    ##

                    completearray.append(new_header)
                    ##
                    #
                    r['type'] = 1
                    r['name'] = r['date_invoice']

                    completearray.append(r)

                if cleanarray[i]['partner_id'] == cleanarray[i-1]['partner_id']:
                    # we reset the counter
                    
                    new_header['amount_total'] = tot_invoice
                    new_header['balance'] = tot_balance
                    new_header['type'] = 3

                    tot_invoice = tot_invoice + r['amount_total']
                    tot_balance = tot_balance + r['balance']

                    new_header['amount_total'] = tot_invoice
                    new_header['balance'] = tot_balance
                    
                    r['type'] = 2
                    r['name'] = r['date_invoice']
                        
                    completearray.append(r)

            i = i + 1
        return completearray

    def _get_asof_date(self, data):
        if data.get('form', False) and data['form'].get('date_as_of', False):
            return data['form']['date_as_of']
        return ''

    def _get_partners(self):

        if self.result_selection == 'customer':
            return _('Receivable Accounts')
        elif self.result_selection == 'supplier':
            return _('Payable Accounts')
        elif self.result_selection == 'customer_supplier':
            return _('Receivable and Payable Accounts')
        return ''


class report_partnerbalance(osv.AbstractModel):
    _name = 'report.account.report_partneroutstanding'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partneroutstanding'
    _wrapped_report_class = partner_outstanding

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
