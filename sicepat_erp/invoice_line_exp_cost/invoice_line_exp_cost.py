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

from openerp import fields, models, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        tax_extra_ship_cost = self.invoice_line_tax_id.compute_all(self.extra_shipping_cost, 1, product=self.product_id, partner=self.invoice_id.partner_id)
        tax_insurance_fee = self.invoice_line_tax_id.compute_all(self.insurance_fee, 1, product=self.product_id, partner=self.invoice_id.partner_id)
        tax_admcost_insurance = self.invoice_line_tax_id.compute_all(self.admcost_insurance, 1, product=self.product_id, partner=self.invoice_id.partner_id)
        tax_packing_cost = self.invoice_line_tax_id.compute_all(self.packing_cost, 1, product=self.product_id, partner=self.invoice_id.partner_id)  
        self.price_subtotal = taxes['total'] + tax_extra_ship_cost['total'] + tax_insurance_fee['total'] + tax_admcost_insurance['total'] + tax_packing_cost['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)

    extra_shipping_cost = fields.Float(string='Extra Shipping Cost', digits= dp.get_precision('Product Price'), default=0.0)
    insurance_value = fields.Float(string='Insurance Value', digits= dp.get_precision('Product Price'), default=0.0)
    insurance_fee = fields.Float(string='Insurance Fee', digits= dp.get_precision('Product Price'), default=0.0)
    admcost_insurance = fields.Float(string='Cost Administration of Insurance', digits= dp.get_precision('Product Price'), default=0.0)
    packing_cost = fields.Float(string='Packing Cost', digits= dp.get_precision('Product Price'), default=0.0)

class account_invoice_tax(models.Model):
    _inherit = "account.invoice.tax"

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            taxes += line.invoice_line_tax_id.compute_all(
                line.extra_shipping_cost, 1, line.product_id, invoice.partner_id)['taxes']
            taxes += line.invoice_line_tax_id.compute_all(
                line.insurance_fee, 1, line.product_id, invoice.partner_id)['taxes']
            taxes += line.invoice_line_tax_id.compute_all(
                line.admcost_insurance, 1, line.product_id, invoice.partner_id)['taxes']
            taxes += line.invoice_line_tax_id.compute_all(
                line.packing_cost, 1, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped
