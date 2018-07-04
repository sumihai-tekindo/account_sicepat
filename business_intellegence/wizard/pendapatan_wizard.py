# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv

class account_chart2(osv.osv_memory):
    """
    For Chart of Accounts
    """
    _name = "account.chart2"
    _description = "Account chart 2"
    _columns = {
        'fiscalyear': fields.many2one('account.fiscalyear', \
                                    'Fiscal year',  \
                                    help='Keep empty for all open fiscal years'),
        'period_from': fields.many2one('account.period', 'Start period'),
        'period_to': fields.many2one('account.period', 'End period'),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                         ('all', 'All Entries'),
                                        ], 'Target Moves', required=True),
    }

    def _get_fiscalyear2(self, cr, uid, context=None):
        """Return default Fiscalyear value"""
        return self.pool.get('account.fiscalyear').find(cr, uid, context=context)

    def onchange_fiscalyear2(self, cr, uid, ids, fiscalyear_id=False, context=None):
        res = {}
        if fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               ORDER BY p.date_start ASC, p.special DESC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods:
                start_period = periods[0]
                if len(periods) > 1:
                    end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period}
        else:
            res['value'] = {'period_from': False, 'period_to': False}
        return res

    def account_chart_open_window2(self, cr, uid, ids, context=None):
        """
        Opens chart of Accounts
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of account chart’s IDs
        @return: dictionary of Open account chart window on given fiscalyear and all Entries or posted entries
        """


        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        period_obj = self.pool.get('account.period')
        fy_obj = self.pool.get('account.fiscalyear')
        bi_revenue_pendapatan_obj   =  self.pool.get('bi.revenue.pendapatan') 
        cr.execute("delete from bi_revenue_pendapatan");

        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        result = mod_obj.get_object_reference(cr, uid, 'business_intellegence', 'action_bi_pendapatan_rpt2')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        fiscalyear_id = data.get('fiscalyear', False) and data['fiscalyear'][0] or False
        result['periods'] = []
        if data['period_from'] and data['period_to']:
            period_from = data.get('period_from', False) and data['period_from'][0] or False
            period_to = data.get('period_to', False) and data['period_to'][0] or False
            result['periods'] = period_obj.build_ctx_periods(cr, uid, period_from, period_to)
        result['context'] = str({'fiscalyear': fiscalyear_id, 'periods': result['periods'], \
                                    'state': data['target_move']})

        period_aw = data['period_from']
        period_ak = data['period_to']
        period_aw = period_aw[0];
        period_ak = period_ak[0];

        # print 'xxxxxxxxxxxxxxxxxxxx_period',period_aw,period_ak;


        date_start = '';
        date_stop = '';
        
        cr.execute("select id,date_start,date_stop from account_period where id >= %s and id <= %s",(period_aw,period_ak,));
        for res in cr.dictfetchall():
            date_start = res['date_start'];
            date_stop = res['date_stop'];      

            # print'xxxxxxxxxxxxxxxxxxxxxx_date',date_start,date_stop;

            cr.execute("select a.date,b.code,b.name as account,c.name as jurnal,a.debit,a.credit, (a.debit - a.credit) as balance from account_move_line a \
            left join account_account b on a.account_id = b.id \
            left join account_journal c on a.journal_id = c.id \
            where b.code like %s and b.type <> %s and a.date >= %s and a.date <= %s",('400.%','view',date_start,date_stop,))
                
            for res in cr.dictfetchall():
                code = '';
                account = '';
                jurnal = '';
                debit = '';
                credit = '';
                balance = '';
                date = '';

                code = res['code']
                account = res['account']
                jurnal = res['jurnal']
                debit = res['debit']
                credit = res['credit']
                balance = res['balance']
                date = res['date']

                # print 'xxxxxxxxxxxxxxxxxx_pendapatan',date,code,account,jurnal,debit,credit,balance;

                bi_revenue_pendapatan_obj.create(cr, uid, {
                    'code': code,
                    'account': account,
                    'jurnal': jurnal,
                    'debit': debit,
                    'credit': credit,
                    'balance': balance,
                    'date': date,
                })

        if fiscalyear_id:
            result['name'] += ':' + fy_obj.read(cr, uid, [fiscalyear_id], context=context)[0]['code']
        return result


    _defaults = {
        'target_move': 'posted',
        'fiscalyear': _get_fiscalyear2,
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
