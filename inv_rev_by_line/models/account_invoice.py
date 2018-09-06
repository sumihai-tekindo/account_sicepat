# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Sicepat Ekspres Indonesia.
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
from openerp.tools.translate import _

class account_invoice(models.Model):
    _inherit = "account.invoice.line"
    _order = "date_invoice desc,sequence,id"
    
    name = fields.Text(index=True)
    date_invoice = fields.Date(related='invoice_id.date_invoice', states={}, store=True, index=True)
    sequence = fields.Integer(index=True)
    inv_line_origin_id = fields.Many2one('account.invoice.line', copy=False)
    inv_line_rev_ids = fields.One2many('account.invoice.line', 'inv_line_origin_id')
    invoice_type = fields.Selection(related='invoice_id.type', store=True, default=False, index=True)
    invoice_state = fields.Selection(related='invoice_id.state', store=True, default=False, index=True)
