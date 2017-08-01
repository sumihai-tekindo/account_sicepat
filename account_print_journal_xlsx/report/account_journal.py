# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 STI (<https://github.com/sumihai-tekindo>).
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
from openerp.addons.account.report.common_report_header import common_report_header
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class journal_print(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(journal_print, self).__init__(cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'time': time,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_account': self._get_account,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_fiscalyear': self._get_fiscalyear,
            'display_currency':self._display_currency,
            'get_target_move': self._get_target_move,
        })

    def set_context(self, objects, data, ids, report_type=None):
        query_params = {}
        move_state = ['draft','posted']
        obj_move = self.pool.get('account.move.line')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
        self.sort_selection = data['form'].get('sort_selection')
        self.target_move = data['form'].get('target_move', 'all')
        self.period_ids = tuple(data['form']['periods'])
        self.journal_ids = tuple(data['form']['journal_ids'])
        if data['form']['filter'] == 'filter_date':
            query_params['date_from'] = data['form']['date_from']
            query_params['date_to'] = data['form']['date_to']
            query = 'AND l.date >= %(date_from)s AND l.date <= %(date_to)s'
            self.filter = self.cr.mogrify(query, query_params)
        else:
            query_params['periods'] = self.period_ids
            query = 'AND l.period_id IN %(periods)s'
            self.filter = self.cr.mogrify(query, query_params)
        if self.target_move == 'posted':
            move_state = ['posted']
        journals = {}
        self.cr.execute('SELECT l.id FROM account_move_line l, account_move am WHERE l.move_id=am.id AND am.state IN %s AND l.journal_id IN %s ' + self.filter + ' AND ' + self.query + ' ORDER BY ' + self.sort_selection + ', l.move_id', (tuple(move_state), self.journal_ids))
        move_lines = ids = map(lambda x: x[0], self.cr.fetchall())
        for move_line in obj_move.browse(self.cr, self.uid, move_lines):
            key = move_line.journal_id.code
            if data['form']['filter'] == 'filter_date':
                key += '-' + move_line.date
            else:
                key += '-' + move_line.period_id.code
            if journals.get(key):
                journals[key]['lines'] += move_line
                journals[key]['debit'] += move_line.debit
                journals[key]['credit'] += move_line.credit
            else:
                journals[key] = dict(key=key,lines=move_line,debit=move_line.debit,credit=move_line.credit,\
                    period_name=data['form']['filter'] == 'filter_date' and move_line.date or move_line.period_id.name,\
                    journal_name=move_line.journal_id.name)

        self.localcontext.update({
                'get_printjournal': lambda : [v for k,v in sorted(journals.items())],
            })
        return super(journal_print, self).set_context(objects, data, ids, report_type=report_type)

    def _display_currency(self, data):
        return data['form']['amount_currency']


class report_printjournal(osv.AbstractModel):
    _name = 'report.account.report_printjournal'
    _inherit = 'report.abstract_report'
    _template = 'account_print_journal_xlsx.report_printjournal'
    _wrapped_report_class = journal_print
