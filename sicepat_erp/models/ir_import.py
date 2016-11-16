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

import csv
import datetime
import itertools
import logging
import operator
import time

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from openerp import api, models, SUPERUSER_ID
from openerp.osv import orm, osv, fields
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, pickle
from openerp.tools.translate import _

import psycopg2
import openerp
from openerp.tools.misc import CountingStream
from openerp.models import fix_import_export_id_paths, PGERROR_TO_OE

FIELDS_RECURSION_LIMIT = 2
ERROR_PREVIEW_BYTES = 200
_logger = logging.getLogger(__name__)

# def invoice_pg(self, cr, uid, fields, data, context=None):
#     cr.execute('SAVEPOINT model_load')
#     messages = []
# 
#     fields = map(fix_import_export_id_paths, fields)
# 
#     fg = self.fields_get(cr, uid, context=context)
#     dg = self.default_get(cr, uid, fg, context=context)
# 
#     ids = []
#     records = []
#     for id, xid, record, info in self._convert_records(cr, uid,
#             self._extract_records(cr, uid, fields, data,
#                                   context=context, log=messages.append),
#             context=context, log=messages.append):
#         try:
#             cr.execute('SAVEPOINT model_load_save')
#         except psycopg2.InternalError, e:
#             # broken transaction, exit and hope the source error was
#             # already logged
#             if not any(message['type'] == 'error' for message in messages):
#                 messages.append(dict(info, type='error',message=
#                     u"Unknown database error: '%s'" % e))
#             break
#         try:
#             records.append(record)
#             cr.execute('RELEASE SAVEPOINT model_load_save')
#         except psycopg2.Warning, e:
#             messages.append(dict(info, type='warning', message=str(e)))
#             cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
#         except psycopg2.Error, e:
#             messages.append(dict(
#                 info, type='error',
#                 **PGERROR_TO_OE[e.pgcode](self, fg, info, e)))
#             # Failed to write, log to messages, rollback savepoint (to
#             # avoid broken transaction) and keep going
#             cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
#         except Exception, e:
#             message = (_('Unknown error during import:') +
#                        ' %s: %s' % (type(e), unicode(e)))
#             moreinfo = _('Resolve other errors first')
#             messages.append(dict(info, type='error',
#                                  message=message,
#                                  moreinfo=moreinfo))
#             # Failed for some reason, perhaps due to invalid data supplied,
#             # rollback savepoint and keep going
#             cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
#     if any(message['type'] == 'error' for message in messages):
#         cr.execute('ROLLBACK TO SAVEPOINT model_load')
#         ids = False
#     else:
#         _logger.info('inserting...')
#         cr.execute("SELECT id FROM wkf WHERE osv='account.invoice' AND on_create=True")
#         wkf_id = (cr.fetchone() or [False])[0]
#         
#         cr.execute("SELECT id FROM wkf_activity WHERE flow_start=True AND wkf_id=%s" % str(wkf_id))
#         activity_id = (cr.fetchone() or [False])[0]
#                 
#         default_values = [
#             ('create_uid', '%s', uid),
#             ('write_uid', '%s', uid),
#             ('create_date', "(now() at time zone 'UTC')"),
#             ('write_date', "(now() at time zone 'UTC')"),
#         ]
#         for record in records:
#             invoice_values = [] + default_values
#             for key in dg:
#                 if key not in record.keys():
#                     record[key]=dg[key]
#             for field in record:
#                 current_field = self._columns[field]
#                 if current_field._classic_write:
#                     invoice_values.append((field, current_field._symbol_set[0], current_field._symbol_set[1](record[field])))
#                 if field == 'partner_id':
#                     partner_id = current_field._symbol_set[1](record[field])
#                 if field == 'date_invoice':
#                     date_invoice = current_field._symbol_set[1](record[field])
# 
#             cr.execute("SELECT id FROM account_invoice WHERE type='out_invoice' AND partner_id="+str(partner_id)+" AND date_invoice='"+str(date_invoice)+"' AND active = true")
#             inv_id = (cr.fetchone() or [False])[0]
#             
#             if not inv_id:
#                 cr.execute("SELECT value FROM ir_values WHERE name='partner_bank_id' AND model='account.invoice' AND key='default' AND key2='type=out_invoice'")
#                 partner_bank_id = (cr.fetchone() or [False])[0]
#                 if partner_bank_id:
#                     partner_bank_id = pickle.loads(partner_bank_id)
#                 invoice_values.append(('partner_bank_id', '%s', str(partner_bank_id)))
#                 
#                 cr.execute("SELECT value FROM ir_values WHERE name='partner_bank2_id' AND model='account.invoice' AND key='default' AND key2='type=out_invoice'")
#                 partner_bank2_id = (cr.fetchone() or [False])[0]
#                 if partner_bank2_id:
#                     partner_bank2_id = pickle.loads(partner_bank2_id)
#                 invoice_values.append(('partner_bank2_id', '%s', str(partner_bank2_id)))
# 
#                 cr.execute("SELECT term.id FROM ir_property property, res_partner partner, account_payment_term term "\
#                     "WHERE property.name like 'property_payment_term' "\
#                     "AND CONCAT('res.partner,', partner.id)=property.res_id "\
#                     "AND CONCAT('account.payment.term,', term.id)=property.value_reference "\
#                     "AND partner.id=%s" % str(partner_id))
#                 payment_term = (cr.fetchone() or [False])[0]
#                 if not payment_term:
#                     cr.execute("SELECT value_reference FROM ir_property "\
#                         "WHERE name='property_payment_term' AND res_id is null")
#                     payment_term = (cr.fetchone() or [False])[0].split(',',)[1]
#                 invoice_values.append(('payment_term', '%s', str(payment_term)))
# 
#                 cr.execute("SELECT commercial_partner_id FROM res_partner WHERE id=%s" % str(partner_id))
#                 commercial_partner_id = (cr.fetchone() or [False])[0]
#                 invoice_values.append(('commercial_partner_id', '%s', str(commercial_partner_id)))
# 
#                 statement = """INSERT INTO "%s" (%s) VALUES(%s) RETURNING id""" % (
#                     "account_invoice",
#                     ', '.join('"%s"' % fname[0] for fname in invoice_values),
#                     ', '.join(fval[1] for fval in invoice_values)
#                 ) 
#                 cr.execute(statement, tuple([u[2] for u in invoice_values if len(u) > 2]))
#                 inv_id, = cr.fetchone()
#                 
#                 cr.execute('INSERT INTO wkf_instance (res_type,res_id,uid,wkf_id,state) values (%s,%s,%s,%s,%s) RETURNING id', ('account.invoice', str(inv_id), uid, str(wkf_id), 'active'))
#                 instance_id, = cr.fetchone()
#                 
#                 cr.execute("INSERT INTO wkf_workitem (act_id,inst_id,state) values (%s,%s,'complete')", (str(activity_id), str(instance_id)))
#             
#             cr.execute("SELECT state FROM account_invoice WHERE id="+str(inv_id))
#             inv_state = (cr.fetchone() or [False])[0]
#             
#             if inv_state != 'draft':
#                 continue
#             
#             for field in record:
#                 if isinstance(record[field], list) and field == 'invoice_line':
#                     for line in record[field]:
#                         invoice_line_values = [] + default_values
#                         invoice_line_values.append(('invoice_id', '%s', inv_id))
#                         invoice_line_values.append(('sequence', '%s', 10))
#                         for fline in line[2]:
#                             line_field = self.pool['account.invoice.line']._columns[fline]
#                             if line_field._classic_write:
#                                 invoice_line_values.append((fline, line_field._symbol_set[0], line_field._symbol_set[1](line[2][fline])))
#                             if fline == 'name':
#                                 name = line_field._symbol_set[1](line[2][fline])
# 
#                         cr.execute("SELECT id FROM account_invoice_line WHERE invoice_id="+str(inv_id)+" AND name='"+name+"'")
#                         line_id = (cr.fetchone() or [False])[0]
#                         if line_id:
#                             # update row
#                             continue
#                         else:
#                             statement = """INSERT INTO "%s" (%s) VALUES(%s) RETURNING id""" % (
#                                 "account_invoice_line",
#                                 ', '.join('"%s"' % fname[0] for fname in invoice_line_values),
#                                 ', '.join(fval[1] for fval in invoice_line_values)
#                             ) 
#                             cr.execute(statement, tuple([u[2] for u in invoice_line_values if len(u) > 2]))
# 
#             ids.append(inv_id)    
#         _logger.info('done inserting')
#         _logger.info('computing %d invoices...', len(ids))
#         for recs in self.browse(cr, uid, ids, context):
#             recs.button_compute()
#             recs.invalidate_cache()
#             _logger.info('computing (%s, %d)' % (self._name, recs.id))
#         _logger.info('done computing')
#         _logger.info('validating...')
#         for recs in self.browse(cr, uid, ids, context):
#             if recs.state not in ('draft', 'proforma', 'proforma2'):
#                 continue
#             recs.signal_workflow('invoice_open')
#             recs.invalidate_cache()
#             _logger.info('validating (%s, %d) with number %s' % (self._name, recs.id, recs.number))
#         _logger.info('done validating')
# #         _logger.info('processing into cron...')
# #         cron_vals = {
# #             'name': 'process_after_action',
# #             'user_id': uid,
# #             'interval_number': 5,
# #             'interval_type': 'minutes',
# #             'numbercall': 1,
# #             'nextcall': datetime.datetime.utcnow().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
# #             'model': self._name,
# #             'function': 'process_after_action',
# #             'args': repr([ids]),
# #             'priority': 5,
# #         }
# #         self.pool['ir.cron'].create(cr, uid, cron_vals)
# #         _logger.info('done processing into cron')
#     return {'ids': ids, 'messages': messages}
# openerp.models.BaseModel.invoice_pg = invoice_pg
    
def load(self, cr, uid, fields, data, context=None):
    """
    Attempts to load the data matrix, and returns a list of ids (or
    ``False`` if there was an error and no id could be generated) and a
    list of messages.

    The ids are those of the records created and saved (in database), in
    the same order they were extracted from the file. They can be passed
    directly to :meth:`~read`

    :param fields: list of fields to import, at the same index as the corresponding data
    :type fields: list(str)
    :param data: row-major matrix of data to import
    :type data: list(list(str))
    :param dict context:
    :returns: {ids: list(int)|False, messages: [Message]}
    """
    cr.execute('SAVEPOINT model_load')
    messages = []

    fields = map(fix_import_export_id_paths, fields)
    ModelData = self.pool['ir.model.data'].clear_caches()

    fg = self.fields_get(cr, uid, context=context)

    mode = 'init'
    current_module = ''
    noupdate = False

    ids = []
    for id, xid, record, info in self._convert_records(cr, uid,
            self._extract_records(cr, uid, fields, data,
                                  context=context, log=messages.append),
            context=context, log=messages.append):
        try:
            cr.execute('SAVEPOINT model_load_save')
        except psycopg2.InternalError, e:
            # broken transaction, exit and hope the source error was
            # already logged
            if not any(message['type'] == 'error' for message in messages):
                messages.append(dict(info, type='error',message=
                    u"Unknown database error: '%s'" % e))
            break
        try:
            if self._name == 'account.invoice' and\
                (context.get('type', False) and context['type'] == 'out_invoice'):
                ids.append(self.pool[self._name]._insert_using_pg(cr, uid, record, context=context))
            else:
                ids.append(ModelData._update(cr, uid, self._name,
                     current_module, record, mode=mode, xml_id=xid,
                     noupdate=noupdate, res_id=id, context=context))
            cr.execute('RELEASE SAVEPOINT model_load_save')
        except psycopg2.Warning, e:
            messages.append(dict(info, type='warning', message=str(e)))
            cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
        except psycopg2.Error, e:
            messages.append(dict(
                info, type='error',
                **PGERROR_TO_OE[e.pgcode](self, fg, info, e)))
            # Failed to write, log to messages, rollback savepoint (to
            # avoid broken transaction) and keep going
            cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
        except Exception, e:
            message = (_('Unknown error during import:') +
                       ' %s: %s' % (type(e), unicode(e)))
            moreinfo = _('Resolve other errors first')
            messages.append(dict(info, type='error',
                                 message=message,
                                 moreinfo=moreinfo))
            # Failed for some reason, perhaps due to invalid data supplied,
            # rollback savepoint and keep going
            cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
    if any(message['type'] == 'error' for message in messages):
        cr.execute('ROLLBACK TO SAVEPOINT model_load')
        ids = False
    return {'ids': ids, 'messages': messages}
openerp.models.BaseModel.load = load

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    def process_after_action(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids):
            if invoice.state not in ('draft', 'proforma', 'proforma2'):
                continue
            invoice.button_compute()
            _logger.info('computing (%s, %d)' % (self._name, invoice.id))
            invoice.signal_workflow('invoice_open')
            _logger.info('validating (%s, %d) with number %s' % (self._name, invoice.id, invoice.number))
#             invoice.action_send_invoice_mail()
            invoice.invalidate_cache()
        return True

    def _insert_using_pg(self, cr, uid, record, context=None):
        fg = self.fields_get(cr, uid, context=context)
        dg = self.default_get(cr, uid, fg, context=context)
        
        cr.execute("SELECT id FROM wkf WHERE osv='account.invoice' AND on_create=True")
        wkf_id = (cr.fetchone() or [False])[0]
        
        cr.execute("SELECT id FROM wkf_activity WHERE flow_start=True AND wkf_id=%s" % str(wkf_id))
        activity_id = (cr.fetchone() or [False])[0]
                
        default_values = [
            ('create_uid', '%s', uid),
            ('write_uid', '%s', uid),
            ('create_date', "(now() at time zone 'UTC')"),
            ('write_date', "(now() at time zone 'UTC')"),
        ]

        invoice_values = [] + default_values
        for key in dg:
            if key not in record.keys():
                record[key]=dg[key]
        for field in record:
            current_field = self._columns[field]
            if current_field._classic_write:
                invoice_values.append((field, current_field._symbol_set[0], current_field._symbol_set[1](record[field])))
            if field == 'partner_id':
                partner_id = current_field._symbol_set[1](record[field])
            if field == 'date_invoice':
                date_invoice = current_field._symbol_set[1](record[field])

        cr.execute("SELECT value FROM ir_values WHERE name='partner_bank_id' AND model='account.invoice' AND key='default' AND key2='type=out_invoice'")
        partner_bank_id = (cr.fetchone() or [False])[0]
        if partner_bank_id:
            partner_bank_id = pickle.loads(partner_bank_id)
        invoice_values.append(('partner_bank_id', '%s', str(partner_bank_id)))
        
        cr.execute("SELECT value FROM ir_values WHERE name='partner_bank2_id' AND model='account.invoice' AND key='default' AND key2='type=out_invoice'")
        partner_bank2_id = (cr.fetchone() or [False])[0]
        if partner_bank2_id:
            partner_bank2_id = pickle.loads(partner_bank2_id)
        invoice_values.append(('partner_bank2_id', '%s', str(partner_bank2_id)))

        cr.execute("SELECT term.id FROM ir_property property, res_partner partner, account_payment_term term "\
            "WHERE property.name like 'property_payment_term' "\
            "AND CONCAT('res.partner,', partner.id)=property.res_id "\
            "AND CONCAT('account.payment.term,', term.id)=property.value_reference "\
            "AND partner.id=%s" % str(partner_id))
        payment_term = (cr.fetchone() or [False])[0]
        if not payment_term:
            cr.execute("SELECT value_reference FROM ir_property "\
                "WHERE name='property_payment_term' AND res_id is null")
            payment_term = (cr.fetchone() or [False])[0].split(',',)[1]
        invoice_values.append(('payment_term', '%s', str(payment_term)))

        cr.execute("SELECT commercial_partner_id FROM res_partner WHERE id=%s" % str(partner_id))
        commercial_partner_id = (cr.fetchone() or [False])[0]
        invoice_values.append(('commercial_partner_id', '%s', str(commercial_partner_id)))

        cr.execute("SELECT id FROM account_invoice WHERE type='out_invoice' AND partner_id="+str(partner_id)+" AND date_invoice='"+str(date_invoice)+"' AND active = true")
        inv_id = (cr.fetchone() or [False])[0]
        
        if inv_id:
            return
#             cr.execute("SELECT state FROM account_invoice WHERE id="+str(inv_id))
#             inv_state = (cr.fetchone() or [False])[0]
#             
#             if inv_state and inv_state not in ('draft', 'proforma', 'proforma2'):
#                 return
        else:
            statement = """INSERT INTO "%s" (%s) VALUES(%s) RETURNING id""" % (
                "account_invoice",
                ', '.join('"%s"' % fname[0] for fname in invoice_values),
                ', '.join(fval[1] for fval in invoice_values)
            ) 
            cr.execute(statement, tuple([u[2] for u in invoice_values if len(u) > 2]))
            inv_id, = cr.fetchone()
            
            cr.execute('INSERT INTO wkf_instance (res_type,res_id,uid,wkf_id,state) values (%s,%s,%s,%s,%s) RETURNING id', ('account.invoice', str(inv_id), uid, str(wkf_id), 'active'))
            instance_id, = cr.fetchone()
            
            cr.execute("INSERT INTO wkf_workitem (act_id,inst_id,state) values (%s,%s,'complete')", (str(activity_id), str(instance_id)))
        
        for field in record:
            if isinstance(record[field], list) and field == 'invoice_line':
                for line in record[field]:
                    invoice_line_values = [] + default_values
                    invoice_line_values.append(('invoice_id', '%s', inv_id))
                    invoice_line_values.append(('sequence', '%s', 10))
                    for fline in line[2]:
                        line_field = self.pool['account.invoice.line']._columns[fline]
                        if line_field._classic_write:
                            invoice_line_values.append((fline, line_field._symbol_set[0], line_field._symbol_set[1](line[2][fline])))
                        if fline == 'name':
                            name = line_field._symbol_set[1](line[2][fline])

                    statement = """INSERT INTO "%s" (%s) VALUES(%s) RETURNING id""" % (
                        "account_invoice_line",
                        ', '.join('"%s"' % fname[0] for fname in invoice_line_values),
                        ', '.join(fval[1] for fval in invoice_line_values)
                    ) 
                    cr.execute(statement, tuple([u[2] for u in invoice_line_values if len(u) > 2]))

        return inv_id
        
class ir_import(orm.TransientModel):
    _inherit = 'base_import.import'
 
    def do(self, cr, uid, id, fields, options, dryrun=False, context=None):
        """ Actual execution of the import
 
        :param fields: import mapping: maps each column to a field,
                       ``False`` for the columns to ignore
        :type fields: list(str|bool)
        :param dict options:
        :param bool dryrun: performs all import operations (and
                            validations) but rollbacks writes, allows
                            getting as much errors as possible without
                            the risk of clobbering the database.
        :returns: A list of errors. If the list is empty the import
                  executed fully and correctly. If the list is
                  non-empty it contains dicts with 3 keys ``type`` the
                  type of error (``error|warning``); ``message`` the
                  error message associated with the error (a string)
                  and ``record`` the data which failed to import (or
                  ``false`` if that data isn't available or provided)
        :rtype: list({type, message, record})
        """
        cr.execute('SAVEPOINT import')
 
        (record,) = self.browse(cr, uid, [id], context=context)
        try:
            data, import_fields = self._convert_import_data(
                record, fields, options, context=context)
        except ValueError, e:
            return [{
                'type': 'error',
                'message': unicode(e),
                'record': False,
            }]
 
        _logger.info('importing %d rows...', len(data))
        import_result = self.pool[record.res_model].load(
            cr, uid, import_fields, data, context=context)
        _logger.info('done')
 
        # If transaction aborted, RELEASE SAVEPOINT is going to raise
        # an InternalError (ROLLBACK should work, maybe). Ignore that.
        # TODO: to handle multiple errors, create savepoint around
        #       write and release it in case of write error (after
        #       adding error to errors array) => can keep on trying to
        #       import stuff, and rollback at the end if there is any
        #       error in the results.
        try:
            if dryrun:
                cr.execute('ROLLBACK TO SAVEPOINT import')
            else:
                if record.res_model == 'account.invoice' and (context.get('type', False) and context['type'] == 'out_invoice'):
                    if import_result['ids']:
                        _logger.info('processing into cron...')
                        for res_id in import_result['ids']:
                            cron_vals = {
                                'name': 'process_after_action',
                                'user_id': SUPERUSER_ID,
                                'interval_number': 1,
                                'interval_type': 'minutes',
                                'numbercall': 1,
                                'doall': True,
                                'nextcall': datetime.datetime.utcnow().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                'model': record.res_model,
                                'function': 'process_after_action',
                                'args': repr([[res_id]]),
                                'priority': 5,
                            }
                            self.pool['ir.cron'].create(cr, SUPERUSER_ID, cron_vals)
                        _logger.info('done processing into cron')
                cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass
 
        return import_result['messages']