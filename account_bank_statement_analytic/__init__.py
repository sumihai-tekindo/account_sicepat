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

from . import models

def update_cash_bank_journal(cr, registry):
    cr.execute('SELECT id FROM account_analytic_journal WHERE type=\'cash\' AND code=\'CSBK\'')
    analytic_journal_id = (cr.fetchone() or [False])[0]
    if analytic_journal_id:
        cr.execute('UPDATE account_journal SET analytic_journal_id=%s WHERE type IN (\'cash\', \'bank\')' % str(analytic_journal_id))