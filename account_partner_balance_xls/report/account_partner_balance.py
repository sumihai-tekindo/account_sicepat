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
from openerp.osv import osv
from openerp.tools.translate import _
# from openerp.report import report_sxw
from openerp.addons.account.report.account_partner_balance import partner_balance as part_bal

class account_move_line(osv.osv):
    _inherit = "account.move.line"
 
    def _domain_get(self, cr, uid, context=None):
        move_obj = self.pool.get('account.move')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalperiod_obj = self.pool.get('account.period')
        account_obj = self.pool.get('account.account')
        domain = []
        fiscalyear_ids = []
        context = dict(context or {})
        initial_bal = context.get('initial_bal', False)
        company_clause = []
        if context.get('company_id'):
            company_clause = [('company_id', '=', context['company_id'])]
        if not context.get('fiscalyear'):
            if context.get('all_fiscalyear'):
                #this option is needed by the aged balance report because otherwise, if we search only the draft ones, an open invoice of a closed fiscalyear won't be displayed
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [])
            else:
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('state', '=', 'draft')])
        else:
            #for initial balance as well as for normal query, we check only the selected FY because the best practice is to generate the FY opening entries
            fiscalyear_ids = context['fiscalyear']
            if isinstance(context['fiscalyear'], (int, long)):
                fiscalyear_ids = [fiscalyear_ids]

        fiscalyear_ids = tuple(fiscalyear_ids) or (0,)
        state = context.get('state', False)
        where_move_state = []
        where_move_lines_by_date = []

        if context.get('date_from') and context.get('date_to'):
            move_ids = []
            if initial_bal:
                move_ids = move_obj.search(cr, uid, [('date', '<', context['date_from'])])
                where_move_lines_by_date = [('move_id', 'in', tuple(move_ids))]
            else:
                move_ids = move_obj.search(cr, uid, [('date', '>=', context['date_from']), ('date', '<=', context['date_to'])])
                where_move_lines_by_date = [('move_id', 'in', tuple(move_ids))]

        if state:
            move_ids = []
            if state.lower() not in ['all']:
                move_ids = move_obj.search(cr, uid, [('state', '=', state)])
                where_move_state= [('move_id', 'in', move_ids)]
        if context.get('period_from') and context.get('period_to') and not context.get('periods'):
            if initial_bal:
                period_company_id = fiscalperiod_obj.browse(cr, uid, context['period_from'], context=context).company_id.id
                first_period = fiscalperiod_obj.search(cr, uid, [('company_id', '=', period_company_id)], order='date_start', limit=1)[0]
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, first_period, context['period_from'])
            else:
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, context['period_from'], context['period_to'])
        if 'periods_special' in context:
            periods_special = [('special', '=', bool(context.get('periods_special')))]
        else:
            periods_special = []
        if context.get('periods'):
            if initial_bal:
                period_ids = fiscalperiod_obj.search(cr, uid, [('fiscalyear_id', 'in', fiscalyear_ids)] + periods_special)
                domain = [('state', '!=', 'draft'), ('period_id', 'in', tuple(period_ids))] + where_move_state + where_move_lines_by_date
                periods = fiscalperiod_obj.search(cr, uid, [('id', 'in', context['periods'])], order='date_start', limit=1)
                if periods and periods[0]:
                    first_period = fiscalperiod_obj.browse(cr, uid, periods[0], context=context)
                    period_ids = fiscalperiod_obj.search(cr, uid, [('fiscalyear_id', 'in', fiscalyear_ids), ('date_start', '<=', first_period.date_start), ('id', 'not in', tuple(context['periods']))] + periods_special)
                    domain = [('state', '!=', 'draft'), ('period_id', 'in', tuple(period_ids))] + where_move_state + where_move_lines_by_date
            else:
                period_ids = fiscalperiod_obj.search(cr, uid, [('fiscalyear_id', 'in', fiscalyear_ids), ('id', 'in', tuple(context['periods']))] + periods_special)
                domain = [('state', '!=', 'draft'), ('period_id', 'in', tuple(period_ids))] + where_move_state + where_move_lines_by_date
        else:
            period_ids = fiscalperiod_obj.search(cr, uid, [('fiscalyear_id', 'in', fiscalyear_ids)] + periods_special)
            domain = [('state', '!=', 'draft'), ('period_id', 'in', tuple(period_ids))] + where_move_state + where_move_lines_by_date

        if initial_bal and not context.get('periods') and not where_move_lines_by_date:
            #we didn't pass any filter in the context, and the initial balance can't be computed using only the fiscalyear otherwise entries will be summed twice
            #so we have to invalidate this query
            raise osv.except_osv(_('Warning!'),_("You have not supplied enough arguments to compute the initial balance, please select a period and a journal in the context."))

        if context.get('journal_ids'):
            domain += [('journal_id', 'in', tuple(context['journal_ids']))]

        if context.get('chart_account_id'):
            if context.get('account_ids'):
                domain += [('account_id', 'in', tuple(context['account_ids']))]
            else:
                child_ids = account_obj._get_children_and_consol(cr, uid, [context['chart_account_id']], context=context)
                domain += [('account_id', 'in', tuple(child_ids))]

        if not context.get('all_partner') and context.get('partner_ids'):
            domain += [('partner_id', 'in', tuple(context['partner_ids']))]
            
        domain += company_clause
        return domain

class partner_balance(part_bal):

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        self.domain = obj_move._domain_get(self.cr, self.uid, context=data['form'].get('used_context', {}))
        self.display_detail = data['form'].get('display_detail')
        res_company = self._get_res_company(data)
        self.localcontext.update({
            'res_company': res_company,
        })
        return super(partner_balance, self).set_context(objects, data, ids, report_type=report_type)
    
    def _get_res_company(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).company_id
        return False

    def lines(self):
        aml_obj = self.pool.get('account.move.line')
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']

        domain = self.domain + [('account_id.type', 'in', self.ACCOUNT_TYPE), ('move_id.state', 'in', tuple(move_state))]
        if self.display_partner == 'non-zero_balance':
            domain += [('reconcile_id', '=', False)]
        full_account = []
        lines = aml_obj.search(self.cr, self.uid, domain, order="account_id, partner_id")
        for line in aml_obj.browse(self.cr, self.uid, lines):
            full_account.append({
                    'ref': line.partner_id.ref or '',
                    'account_id': line.account_id.id,
                    'account_name': line.account_id.name,
                    'code': line.account_id.code,
                    'name': line.partner_id and line.partner_id.name or False,
                    'debit': line.debit,
                    'credit': line.credit,
#                     'sdebit': (line.debit > line.credit) and (line.debit - line.credit) or 0,
#                     'scredit': (line.debit < line.credit) and (line.credit - line.debit) or 0,
                    'enlitige': line.blocked and (line.debit - line.credit) or 0,
                    'date': line.date,
                    'move_name': line.move_id.name,
                })

        ## We will now compute Total
        subtotal_row = self._group_subtotal(sorted(full_account, key=lambda k: (k['code'], k['name'], k['date'])))
        for rec in subtotal_row:
            if not rec.get('name', False):
                rec.update({'name': _('Unknown Partner')})

        return subtotal_row

    def _group_subtotal(self, cleanarray):
        res_dict = {}
        for line in cleanarray:
            group_account = line['code']
            group_partner = line['name'] or ''
            group_move = line['date'] + '-' + line['move_name']
            key_level_account = group_account
            key_level_partner = key_level_account + '-' + group_partner
            key_level_move = key_level_partner + '-' + group_move
            if self.display_detail:
                if res_dict.get(key_level_move):
                    res_dict[key_level_move]['debit'] += line['debit']
                    res_dict[key_level_move]['credit'] += line['credit']
                    res_dict[key_level_move]['balance'] += (line['debit']-line['credit'])
                    res_dict[key_level_move]['enlitige'] += line['enlitige']
                else:
                    res_dict[key_level_move] = dict(line, type=1, balance=(line['debit']-line['credit']))
            if res_dict.get(key_level_partner):
                res_dict[key_level_partner]['debit'] += line['debit']
                res_dict[key_level_partner]['credit'] += line['credit']
                res_dict[key_level_partner]['balance'] += (line['debit']-line['credit'])
                res_dict[key_level_partner]['enlitige'] += line['enlitige']
            else:
                res_dict[key_level_partner] = {
                        'type': 2,
                        'ref': line['ref'],
                        'code': line['code'],
                        'name': line['name'],
                        'debit': line['debit'],
                        'credit': line['credit'],
                        'balance': (line['debit']-line['credit']),
                        'enlitige': line['enlitige'],
                    }
            if res_dict.get(key_level_account):
                res_dict[key_level_account]['debit'] += line['debit']
                res_dict[key_level_account]['credit'] += line['credit']
                res_dict[key_level_account]['balance'] += (line['debit']-line['credit'])
                res_dict[key_level_account]['enlitige'] += line['enlitige']
            else:
                res_dict[key_level_account] = {
                        'type': 3,
                        'ref': '',
                        'code': line['code'],
                        'name': line['account_name'],
                        'debit': line['debit'],
                        'credit': line['credit'],
                        'balance': (line['debit']-line['credit']),
                        'enlitige': line['enlitige'],
                    }

#         if self.display_partner == 'non-zero_balance':
#             for k, v in res_dict.items():
#                 if v.get('balance') <= 0:
#                     res_dict.pop(k)

        return [v for k, v in sorted(res_dict.items())]
        
class report_partnerbalance(osv.AbstractModel):
    _name = 'report.account.report_partnerbalance'
    _inherit = 'report.abstract_report'
    _template = 'account.report_partnerbalance'
    _wrapped_report_class = partner_balance

