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

from openerp import fields, models, api
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_invoice(models.Model):
    # Private attributes
    _inherit = "account.invoice"

    # Default methods
    @api.one
    @api.depends('invoice_line.price_unit', 'invoice_line.quantity')
    def _compute_additional_total(self):
        self.price_unit_total = sum((line.quantity * line.price_unit) + line.insurance_fee + line.admcost_insurance + line.packing_cost for line in self.invoice_line)

    @api.one
    @api.depends('amount_total', 'outstanding', 'overpaid')
    def _compute_amount_plus(self):
        self.amount_total_plus = self.amount_total + self.outstanding + self.overpaid

    @api.one
    @api.depends(
        'state', 'currency_id', 'partner_id', 'date_invoice', 'invoice_line.price_subtotal',
        'move_id.line_id.account_id.type',
        'move_id.line_id.amount_residual',
        # Fixes the fact that move_id.line_id.amount_residual, being not stored and old API, doesn't trigger recomputation
        'move_id.line_id.reconcile_id',
        'move_id.line_id.amount_residual_currency',
        'move_id.line_id.currency_id',
        'move_id.line_id.reconcile_partial_id.line_partial_ids.invoice.type',
    )
    # An invoice's outstanding amount is the sum of its residual amount
    def _compute_outstanding(self):
        filters = [('state', '=', 'open'), ('partner_id', '=', self.partner_id.id)]
        for inv in self.search(filters):
            if inv.id == self.id:
                continue
            if inv.date_invoice > (self.date_invoice if self.date_invoice else fields.Date.context_today(inv)):
                continue
            if inv.currency_id == self.currency_id:
                residual = inv.residual
            else:
                from_currency = inv.company_id.currency_id.with_context(date=inv.date_invoice)
                residual = from_currency.compute(inv.residual, self.currency_id)
            self.outstanding += residual
        self.outstanding = max(self.outstanding, 0.0)

#         outstanding = 0.0
#         if not self.id:
#             self.oustanding = outstanding
#         date_invoice = self.date_invoice
#         if not self.date_invoice:
#             date_invoice = fields.Date.context_today(self)
#         query = """ SELECT inv2.id
#                     FROM account_invoice inv1, account_invoice inv2
#                     WHERE
#                         inv2.partner_id=inv1.partner_id AND 
#                         inv2.date_invoice<=%s AND
#                         inv2.state='open' AND
#                         inv2.id<>inv1.id AND
#                         inv1.id=%s
#                 """
#         self._cr.execute(query, (date_invoice, self.id,))
#         inv_ids = [row[0] for row in self._cr.fetchall()]
#         if not inv_ids:
#             self.oustanding = outstanding
#         for inv in self.browse(inv_ids):
#             if inv.currency_id == self.currency_id:
#                 residual = inv.residual
#             else:
#                 from_currency = inv.company_id.currency_id.with_context(date=inv.date_invoice)
#                 residual = from_currency.compute(inv.residual, self.currency_id)
#             outstanding += residual
#         print('outstanding[%s]: %s' % (self.id, outstanding))
#         self.outstanding = max(outstanding, 0.0)

#         self.outstanding = self.test_outstanding()

    @api.one
    @api.depends(
        'state', 'currency_id', 'partner_id', 'date_invoice', 'invoice_line.price_subtotal',
        'move_id.line_id.account_id.type',
        'move_id.line_id.amount_residual',
        # Fixes the fact that move_id.line_id.amount_residual, being not stored and old API, doesn't trigger recomputation
        'move_id.line_id.reconcile_id',
        'move_id.line_id.amount_residual_currency',
        'move_id.line_id.currency_id',
        'move_id.line_id.reconcile_partial_id.line_partial_ids.invoice.type',
    )
    # An invoice's outstanding amount is the sum of its residual amount
    def _compute_overpaid(self):
        self.overpaid = self.test_overpaid()

    # Fields declaration
    price_unit_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_additional_total')
    outstanding = fields.Float(string='Outstanding Balance', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_outstanding', help="Outstanding amount due.")
    overpaid = fields.Float(string='Overpaid Balance', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_overpaid', help="Overpaid amount.")
    amount_total_plus = fields.Float(string='Total Due', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount_plus')

    @api.multi
    def invoice_id_residual_get(self):
        # Deprecated
        if not self.id:
            return []
        date_invoice = self.date_invoice
        if not self.date_invoice:
            date_invoice = fields.Date.context_today(self)
        query = """ SELECT id
                    FROM account_invoice
                    WHERE id <> %s AND state = 'open' AND partner_id = %s AND date_invoice <= %s
                """
        self._cr.execute(query, (self.id, self.partner_id.id, date_invoice,))
        return [row[0] for row in self._cr.fetchall()]

    @api.multi
    def test_outstanding(self):
        # Deprecated
        outstanding = 0.0
        inv_ids = self.invoice_id_residual_get()
        if not inv_ids:
            return outstanding
        for inv in self.browse(inv_ids):
            if inv.currency_id == self.currency_id:
                residual = inv.residual
            else:
                from_currency = inv.company_id.currency_id.with_context(date=inv.date_invoice)
                residual = from_currency.compute(inv.residual, self.currency_id)
            outstanding += residual
        return max(outstanding, 0.0)

    @api.multi
    def move_line_id_overpaid_get(self):
        # return the move line ids with the same account, same partner as the invoice self
        if not self.id:
            return []
        date_invoice = self.date_invoice
        if not self.date_invoice:
            date_invoice = fields.Date.context_today(self)
        query = """ SELECT move_line.id
                    FROM account_move_line move_line, account_invoice inv, account_account acc
                    WHERE
                        move_line.partner_id=inv.partner_id AND 
                        move_line.account_id=acc.id AND 
                        acc.type='receivable' AND
                        move_line.credit>0 AND
                        move_line.reconcile_ref is null AND
                        move_line.date<=%s AND
                        inv.id=%s
                """
        self._cr.execute(query, (date_invoice, self.id,))
        return [row[0] for row in self._cr.fetchall()]

    @api.multi
    def test_overpaid(self):
        overpaid = 0.0
        move_line_ids = self.move_line_id_overpaid_get()
        if not move_line_ids:
            return overpaid
        for move_line in self.env['account.move.line'].browse(move_line_ids):
            if move_line.currency_id == self.currency_id:
                overpaid_amount = move_line.amount_currency if move_line.currency_id else move_line.credit
            else:
                from_currency = move_line.company_id.currency_id.with_context(date=move_line.date)
                overpaid_amount = from_currency.compute(move_line.credit, self.currency_id)
            overpaid -= overpaid_amount
        return min(overpaid, 0.0)

    def remove_after_process(self, cr, uid, cron_ids=None):
        if not cron_ids:
            cr.execute("""SELECT id FROM ir_cron
                          WHERE numbercall = 0
                              AND not active AND nextcall <= (now() at time zone 'UTC')
                              AND model = 'account.invoice' AND name = 'process_after_action'""")
            cron_ids = [cron_id[0] for cron_id in cr.fetchall()]
            if not cron_ids:
                _logger.info('no cron\'s inactive')
                return
        self.pool['ir.cron'].unlink(cr, uid, cron_ids)
        return True

class account_move(osv.osv):
    _inherit = "account.move"

    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        date_invoice = False
        if invoice and invoice.date_invoice:
            date_invoice = invoice.date_invoice
        valid_moves = self.validate(cr, uid, ids, context)

        if not valid_moves:
            raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
        obj_sequence = self.pool.get('ir.sequence')
        for move in self.browse(cr, uid, valid_moves, context=context):
            if move.name =='/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id, 'ir_sequence_date': date_invoice}
                        new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                    else:
                        raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))

                if new_name:
                    self.write(cr, uid, [move.id], {'name':new_name})

        cr.execute('UPDATE account_move '\
                   'SET state=%s '\
                   'WHERE id IN %s',
                   ('posted', tuple(valid_moves),))
        self.invalidate_cache(cr, uid, ['state', ], valid_moves, context=context)
        return True