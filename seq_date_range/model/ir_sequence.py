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

import pytz
from datetime import date, datetime, timedelta

import openerp
from openerp.osv import fields, osv
from openerp.tools.translate import _

def _create_sequence(self, cr, uid, seq_name, number_increment, number_next, context=None):
    """ Create a PostreSQL sequence.

    There is no access rights check.
    """
    if number_increment == 0:
        raise osv.except_osv(_('Warning!'),_("Increment number must not be zero."))
    sql = "CREATE SEQUENCE %s INCREMENT BY %%s START WITH %%s" % seq_name
    cr.execute(sql, (number_increment, number_next))

def _drop_sequence(self, cr, uid, seq_names, context=None):
    """ Drop the PostreSQL sequence if it exists.

    There is no access rights check.
    """
    names = []
    for n in seq_names:
        names.append(n)
    names = ','.join(names)
    # RESTRICT is the default; it prevents dropping the sequence if an
    # object depends on it.
    cr.execute("DROP SEQUENCE IF EXISTS %s RESTRICT " % names)

def _alter_sequence(self, cr, uid, seq_name, number_increment=None, number_next=None, context=None):
    """ Alter a PostreSQL sequence.

    There is no access rights check.
    """
    if number_increment == 0:
        raise osv.except_osv(_('Warning!'),_("Increment number must not be zero."))
    cr.execute("SELECT relname FROM pg_class WHERE relkind = %s AND relname=%s", ('S', seq_name))
    if not cr.fetchone():
        # sequence is not created yet, we're inside create() so ignore it, will be set later
        return
    statement = "ALTER SEQUENCE %s" % (seq_name, )
    if number_increment is not None:
        statement += " INCREMENT BY %d" % (number_increment, )
    if number_next is not None:
        statement += " RESTART WITH %d" % (number_next, )
    cr.execute(statement)

def _select_nextval(self, cr, uid, seq_name, context=None):
    cr.execute("SELECT nextval('%s')" % seq_name)
    return cr.fetchone()

def _update_nogap(self, cr, uid, sequence, number_increment, context=None):
    number_next = sequence['number_next']
    cr.execute("SELECT number_next FROM %s WHERE id=%s FOR UPDATE NOWAIT" % (self._table, sequence['id']))
    cr.execute("UPDATE %s SET number_next=number_next+%s WHERE id=%s " % (self._table, number_increment, sequence['id']))
    return number_next

def _get_first_day(self, cr, uid, dt, d_years=0, d_months=0, context=None):
    # d_years, d_months are "deltas" to apply to dt
    dt = datetime.strptime(dt, '%Y-%m-%d')
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return date(y+a, m+1, 1)

def _get_last_day(self, cr, uid, dt, context=None):
    return _get_first_day(self, cr, uid, dt, 0, 1) + timedelta(-1)

class ir_sequence(openerp.osv.osv.osv):
    """ Sequence model.

    The sequence model allows to define and use so-called sequence objects.
    Such objects are used to generate unique identifiers in a transaction-safe
    way.

    """
    _inherit = 'ir.sequence'
    
    _columns = {
        'use_date_range': openerp.osv.fields.boolean('Use subsequences per date_range'),
        'date_range_type': openerp.osv.fields.selection([
            ('yearly', 'Yearly'),
            ('monthly', 'Monthly'),
            ('daily', 'Daily')
            ], 'Date Range Type'),
        'date_range_ids': openerp.osv.fields.one2many('ir.sequence.date_range', 'sequence_id', 'Subsequences'),
    }

    _defaults = {
        'date_range_type': 'yearly',
    }
    
    def create(self, cr, uid, values, context=None):
        """ Create a sequence, in implementation == standard a fast gaps-allowed PostgreSQL sequence is used.
        """
        values = self._add_missing_default_values(cr, uid, values, context)
        seq = osv.osv.create(self, cr, uid, values, context)
        if values['implementation'] == 'standard':
            _create_sequence(self, cr, uid, "ir_sequence_%03d" % seq, values.get('number_increment', 1), values.get('number_next', 1))
        return seq
    
    def unlink(self, cr, uid, ids, context=None):
        _drop_sequence(self, cr, uid, ["ir_sequence_%03d" % x.id for x in self.browse(cr, uid, ids, context=context)])
        return osv.osv.unlink(self, cr, uid, ids, context)
    
    def write(self, cr, uid, ids, values, context=None):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        new_implementation = values.get('implementation')
        rows = self.read(cr, uid, ids, ['implementation', 'number_increment', 'number_next', 'date_range_ids'], context)
        osv.osv.write(self, cr, uid, ids, values, context)
    
        for row in rows:
            # 4 cases: we test the previous impl. against the new one.
            i = values.get('number_increment', row['number_increment'])
            n = values.get('number_next', row['number_next'])
            if row['implementation'] == 'standard':
                if new_implementation in ('standard', None):
                    # Implementation has NOT changed.
                    # Only change sequence if really requested.
                    if values.get('number_next'):
                        _alter_sequence(self, cr, uid, "ir_sequence_%03d" % row['id'], number_next=n)
                    if row['number_increment'] != i:
                        _alter_sequence(self, cr, uid, "ir_sequence_%03d" % row['id'], number_increment=i)
                        self.pool.get('ir.sequence.date_range')._alter_sequence(cr, uid, [x.id for x in row['date_range_ids']], number_increment=i)
                else:
                    _drop_sequence(self, cr, uid, ["ir_sequence_%03d" % row['id']])
                    for sub_seq in row['date_range_ids']:
                        _drop_sequence(self, cr, uid, ["ir_sequence_%03d_%03d" % (row['id'], sub_seq.id)])
            else:
                if new_implementation in ('no_gap', None):
                    pass
                else:
                    _create_sequence(self, cr, uid, "ir_sequence_%03d" % row['id'], i, n)
                    for sub_seq in row['date_range_ids']:
                        _create_sequence(self, cr, uid, "ir_sequence_%03d_%03d" % (row['id'], sub_seq.id), i, n)
    
        return True
    
    def _next(self, cr, uid, ids, context=None):
        date_range_obj = self.pool.get('ir.sequence.date_range')
        if not ids:
            return False
        if context is None:
            context = {}
        force_company = context.get('force_company')
        if not force_company:
            force_company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        sequences = self.read(cr, uid, ids, ['name','company_id','implementation','number_next','prefix','suffix','padding','number_increment','use_date_range','date_range_type'])
        preferred_sequences = [s for s in sequences if s['company_id'] and s['company_id'][0] == force_company ]
        seq = preferred_sequences[0] if preferred_sequences else sequences[0]
        if not seq['use_date_range']:
            return self._next_do(cr, uid, seq, context=context)
        # date mode
        dt = fields.date.context_today(self, cr, uid, context=context)
        if context.get('ir_sequence_date'):
            dt = context.get('ir_sequence_date')
        seq_date_id = (date_range_obj.search(cr, uid, [('sequence_id', '=', seq['id']), ('date_from', '<=', dt), ('date_to', '>=', dt)], limit=1) or [False])[0]
        if not seq_date_id:
            seq_date_id = self._create_date_range_seq(cr, uid, seq, dt, context=context)
        return date_range_obj._next(cr, uid, seq_date_id, seq, context=context)
        
    def _next_do(self, cr, uid, sequence, context=None):
        if sequence['implementation'] == 'standard':
            number_next = _select_nextval(self, cr, uid, 'ir_sequence_%03d' % sequence['id'], context=context)
        else:
            number_next = _update_nogap(self, cr, uid, sequence, sequence['number_increment'], context=context)
        return self.get_next_char(cr, uid, sequence, number_next, context=context)

    def get_next_char(self, cr, uid, sequence, number_next, context=None):
        def _interpolate(s, d):
            if s:
                return s % d
            return ''

        def _interpolation_dict():
            now = datetime.now(pytz.timezone(context.get('tz') or 'UTC'))
            if context.get('ir_sequence_date'):
                t = datetime.strptime(context.get('ir_sequence_date'), '%Y-%m-%d')
            else:
                t = now
            
            legends = {
                'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
                'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S'
            }
            res = {}
            for key, legend in legends.iteritems():
                res[key] = now.strftime(legend)
                res['range_' + key] = t.strftime(legend)

            return res

        d = _interpolation_dict()
        try:
            interpolated_prefix = _interpolate(sequence['prefix'], d)
            interpolated_suffix = _interpolate(sequence['suffix'], d)
        except ValueError:
            raise osv.except_osv(_('Warning'), _('Invalid prefix or suffix for sequence \'%s\'') % (sequence.get('name')))
        return interpolated_prefix + '%%0%sd' % sequence['padding'] % number_next + interpolated_suffix

    def _create_date_range_seq(self, cr, uid, sequence, date, context=None):
        date_range_obj = self.pool.get('ir.sequence.date_range')
        year = datetime.strptime(date, '%Y-%m-%d').strftime('%Y')
        date_from = '{}-01-01'.format(year)
        date_to = '{}-12-31'.format(year)
        if sequence['date_range_type'] == 'monthly':
            date_from = _get_first_day(self, cr, uid, date).strftime('%Y-%m-%d')
#             date_from = date_from.strftime('%Y-%m-%d')
            date_to = _get_last_day(self, cr, uid, date).strftime('%Y-%m-%d')
#             date_to = date_to.strftime('%Y-%m-%d')
        elif sequence['date_range_type'] == 'daily':
            date_from = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
            date_to = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
        date_range_ids = date_range_obj.search(cr, uid, [('sequence_id', '=', sequence['id']), ('date_from', '>=', date), ('date_from', '<=', date_to)], order='date_from desc')
        if date_range_ids:
            date_range = date_range_obj.browse(cr, uid, date_range_ids)[0]
            date_to = datetime.strptime(date_range.date_from, '%Y-%m-%d') + timedelta(days=-1)
            date_to = date_to.strftime('%Y-%m-%d')
        date_range_ids = date_range_obj.search(cr, uid, [('sequence_id', '=', sequence['id']), ('date_to', '>=', date_from), ('date_to', '<=', date)], order='date_to desc')
        if date_range_ids:
            date_range = date_range_obj.browse(cr, uid, date_range_ids)[0]
            date_from = datetime.strptime(date_range.date_to, '%Y-%m-%d') + timedelta(days=1)
            date_from = date_from.strftime('%Y-%m-%d')
        seq_date_range = date_range_obj.create(cr, uid, {
            'date_from': date_from,
            'date_to': date_to,
            'sequence_id': sequence['id'],
        })
        return seq_date_range

class ir_sequence_date_range(openerp.osv.osv.osv):
    _name = 'ir.sequence.date_range'
    _rec_name = "sequence_id"

    def _get_number_next_actual(self, cr, user, ids, field_name, arg, context=None):
        '''Return number from ir_sequence_date_range row when no_gap implementation,
        and number from postgres sequence when standard implementation.'''
        res = dict.fromkeys(ids)
        for element in self.browse(cr, user, ids, context=context):
            if element.sequence_id.implementation != 'standard':
                res[element.id] = element.number_next
            else:
                # get number from postgres sequence. Cannot use
                # currval, because that might give an error when
                # not having used nextval before.
                statement = (
                    "SELECT last_value, increment_by, is_called"
                    " FROM ir_sequence_%03d_%03d"
                    % (element.sequence_id.id, element.id))
                cr.execute(statement)
                (last_value, increment_by, is_called) = cr.fetchone()
                if is_called:
                    res[element.id] = last_value + increment_by
                else:
                    res[element.id] = last_value
        return res

    def _set_number_next_actual(self, cr, uid, id, name, value, args=None, context=None):
        return self.write(cr, uid, id, {'number_next': value or 0}, context=context)

    _columns = {
        'date_from': openerp.osv.fields.date('From', required=True),
        'date_to': openerp.osv.fields.date('To', required=True),
        'sequence_id': openerp.osv.fields.many2one('ir.sequence', 'Main Sequence', required=True, ondelete='cascade'),
        'number_next': openerp.osv.fields.integer('Next Number', required=True, help="Next number of this sequence"),
        'number_next_actual': openerp.osv.fields.function(_get_number_next_actual, fnct_inv=_set_number_next_actual, type='integer', required=True, string='Next Number', help='Next number that will be used. This number can be incremented frequently so the displayed value might already be obsolete'),
    }
    
    _defaults = {
        'number_next': 1,
        'number_next_actual': 1,
    }

    def _next(self, cr, uid, seq_date_id, sequence, context=None):
        if context is None:
            context = {}
        sequence_obj = self.pool.get('ir.sequence')
        seq_date = self.browse(cr, uid, seq_date_id, context=context)[0]
        if sequence['implementation'] == 'standard':
            number_next = _select_nextval(self, cr, uid, 'ir_sequence_%03d_%03d' % (sequence['id'], seq_date_id), context=context)
        else:
            number_next = _update_nogap(self, cr, uid, seq_date, sequence['number_increment'], context=context)
        dict(context).update({'ir_sequence_date_range': seq_date.date_from})
        return sequence_obj.get_next_char(cr, uid, sequence, number_next, context=context)

    def _alter_sequence(self, cr, uid, ids, number_increment=None, number_next=None):
        for seq in self.browse(cr, uid, ids):
            _alter_sequence(self, cr, uid, "ir_sequence_%03d_%03d" % (seq.sequence_id.id, seq.id), number_increment=number_increment, number_next=number_next)

    def create(self, cr, uid, values, context=None):
        """ Create a sequence, in implementation == standard a fast gaps-allowed PostgreSQL sequence is used.
        """
        seq = super(ir_sequence_date_range, self).create(cr, uid, values, context=context)
        main_seq = self.browse(cr, uid, seq, context=context).sequence_id
        if main_seq.implementation == 'standard':
            _create_sequence(self, cr, uid, "ir_sequence_%03d_%03d" % (main_seq.id, seq), main_seq.number_increment, values.get('number_next_actual', 1))
        return seq

    def unlink(self, cr, uid, ids, context=None):
        _drop_sequence(self, cr, uid, ["ir_sequence_%03d_%03d" % (x.sequence_id.id, x.id) for x in self.browse(cr, uid, ids, context=context)])
        return super(ir_sequence_date_range, self).unlink(cr, uid, ids, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        seq_to_alter_ids = []
        if values.get('number_next'):
            for seq in self.browse(cr, uid, ids, context=context):
                if seq.sequence_id.implementation == 'standard':
                    seq_to_alter_ids.append(seq.id)
            self._alter_sequence(cr, uid, seq_to_alter_ids, number_next=values.get('number_next'))
        return super(ir_sequence_date_range, self).write(cr, uid, ids, values, context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
