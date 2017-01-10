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

from openerp import api
from openerp.osv import osv, fields
from openerp.osv.expression import get_unaccent_wrapper

class account_invoice(osv.Model):
    _inherit = "account.invoice"

    _columns = {
        'department_id': fields.many2one('account.invoice.department', 'Department', copy=False, ondelete='set null'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        obj_sequence = self.pool.get('ir.sequence')
        obj_journal = self.pool.get('account.journal')
        obj_dept = self.pool.get('account.invoice.department')
        number = ''
        journal = self._default_journal(cr, uid, context)
        date_invoice = vals.get('date_invoice', fields.date.context_today(self, cr, uid, context))
        
        if vals.get('journal_id') and vals['journal_id']:
            journal = obj_journal.browse(cr, uid, vals['journal_id'])

        if vals.get('department_id') and vals['department_id']:
            department = obj_dept.browse(cr, uid, vals['department_id'])
        
        if context.get('type', False) in ('in_invoice', 'in_refund') or (vals.get('type') and vals['type'] in ('in_invoice', 'in_refund')):
            if journal.sequence_id:
                ctx = dict(context)
                ctx['ir_sequence_date'] = date_invoice
                number = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, ctx)
            else:
                raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))
            if number:
                number = "%s/%s" % (department.name, number)
                vals['internal_number'] = number

        res_id = super(account_invoice, self).create(cr, uid, vals, context)
        if context.get('type', False) in ('in_invoice', 'in_refund') or (vals.get('type') and vals['type'] in ('in_invoice', 'in_refund')):
            self.write(cr, uid, [res_id], {'number': number})
        return res_id

    @api.multi
    def action_cancel(self):
        res = super(account_invoice, self).action_cancel()
        if self.type in ('in_invoice', 'in_refund'):
            self.write({'number': self.internal_number})
        return res

class account_invoice_department(osv.Model):
    _name = "account.invoice.department"
    _order = "description asc"
    
    _columns = {
        'name': fields.char('Code', size=4, required=True, copy=False),
        'description': fields.char('Description'),
        'active': fields.boolean('Active'),
    }
    
    _defaults = {
        'active': True,
    }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if context.get('description_only'):
                name = record.description
            res.append((record.id, name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):

            self.check_access_rights(cr, uid, 'read')
            where_query = self._where_calc(cr, uid, args, context=context)
            self._apply_ir_rules(cr, uid, where_query, 'read', context=context)
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(cr)

            query = """SELECT id
                         FROM account_invoice_department
                      {where} ({name} {operator} {percent}
                           OR {description} {operator} {percent})
                     ORDER BY {description}
                    """.format(where=where_str, operator=operator,
                               name=unaccent('name'),
                               description=unaccent('description'),
                               percent=unaccent('%s'))

            where_clause_params += [search_name, search_name]
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            cr.execute(query, where_clause_params)
            ids = map(lambda x: x[0], cr.fetchall())

            if ids:
                return self.name_get(cr, uid, ids, context)
            else:
                return []
        return super(account_invoice_department,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)
