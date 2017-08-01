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

from openerp.addons.account.wizard.account_report_common_journal import account_common_journal_report
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class account_print_journal_xlsx(osv.osv_memory):
    _inherit = 'account.print.journal'
    _name = 'account.print.journal.xlsx'
    _description = 'Account Print Journal XLSX'

    _columns = {
        'report_type': fields.selection([
            ('xlsx','XLSX'),
            ('pdf','PDF')
            ], 'Report Type', required=True),
        'journal_ids': fields.many2many('account.journal', 'account_print_journal_xlsx_rel', 'account_id', 'journal_id', 'Journals', required=True),
    }
    _defaults = {
        'report_type': 'xlsx',
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """ skip account.common.journal.report,fields_view_get
        (adds domain filter on journal type)  """
        return super(account_common_journal_report, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['sort_selection','report_type'], context=context)[0])
        data['form'].update({'periods': list(set(data['form']['periods']))})
        data['form']['used_context'].update({'periods': list(set(data['form']['used_context']['periods']))})
        move_state = ['draft','posted']
        if data['form']['target_move'] == 'posted':
            move_state = ['posted']
        sort_selection = 'date'
        if data['form']['sort_selection'] == 'am.name':
            sort_selection = 'move_id'
        fy_ids = data['form']['fiscalyear_id'] and [data['form']['fiscalyear_id']] or self.pool.get('account.fiscalyear').search(cr, uid, [('state', '=', 'draft')])
        period_list = data['form']['periods'] or self.pool.get('account.period').search(cr, uid, [('fiscalyear_id', 'in', fy_ids)])
        domain = [('journal_id', 'in', data['form']['journal_ids']), ('move_id.state', 'in', tuple(move_state))]
        if data['form']['filter'] == 'filter_date':
            domain += [('date', '>=', data['form']['date_from']), ('date', '<=', data['form']['date_to'])]
        else:
            domain += [('period_id', 'in', period_list)]
        aml_ids = self.pool.get('account.move.line').search(cr, uid, domain, order='journal_id, %s' % (sort_selection))
        data.update({'model': 'account.move.line'})
        data.update({'ids': aml_ids})
        data['form'].update({'active_ids': aml_ids})
#         print('data: %s' % data)
#         return {'type': 'ir.actions.act_window_close'}
        if data['form']['report_type'] == 'xlsx':
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'account.report_printjournal_xlsx',
                    'datas': data
                }
        else:
            context['landscape'] = True
            return self.pool['report'].get_action(cr, uid, [], 'account.report_printjournal', data=data, context=context)
