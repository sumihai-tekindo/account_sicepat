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

import math

from openerp.osv import osv
from openerp.addons.base.ir.ir_qweb import HTMLSafe

class MonetaryConverter(osv.AbstractModel):
    _inherit = 'ir.qweb.field.monetary'

    def record_to_html(self, cr, uid, field_name, record, options, context=None):
        if context is None:
            context = {}
        Currency = self.pool['res.currency']
        display_currency = self.display_currency(cr, uid, options['display_currency'], options)

        # lang.format mandates a sprintf-style format. These formats are non-
        # minimal (they have a default fixed precision instead), and
        # lang.format will not set one by default. currency.round will not
        # provide one either. So we need to generate a precision value
        # (integer > 0) from the currency's rounding (a float generally < 1.0).
        #
        # The log10 of the rounding should be the number of digits involved if
        # negative, if positive clamp to 0 digits and call it a day.
        # nb: int() ~ floor(), we want nearest rounding instead
        precision = int(math.floor(math.log10(display_currency.rounding)))
        if options.get('no_rounding', False):
            precision = 0
        fmt = "%.{0}f".format(-precision if precision < 0 else 0)

        from_amount = record[field_name]

        if options.get('from_currency'):
            from_currency = self.display_currency(cr, uid, options['from_currency'], options)
            from_amount = Currency.compute(cr, uid, from_currency.id, display_currency.id, from_amount)

        lang_code = context.get('lang') or 'en_US'
        lang = self.pool['res.lang']
        formatted_amount = lang.format(cr, uid, [lang_code],
            fmt, Currency.round(cr, uid, display_currency, from_amount),
            grouping=True, monetary=True)

        pre = post = u''
        if display_currency.position == 'before':
            pre = u'{symbol}\N{NO-BREAK SPACE}'
        else:
            post = u'\N{NO-BREAK SPACE}{symbol}'

        return HTMLSafe(u'{pre}<span class="oe_currency_value">{0}</span>{post}'.format(
            formatted_amount,
            pre=pre, post=post,
        ).format(
            symbol=display_currency.symbol,
        ))