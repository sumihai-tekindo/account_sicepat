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

import logging
import time

_logger = logging.getLogger(__name__)

def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.

    Without this script, if a database has a few hundred thousand
    invoice lines, which is not unlikely, the update will take
    at least a few hours.

    The pre init script only writes 0 in the field maturity_residual
    so that it is not computed by the install.

    The post init script sets the value of maturity_residual.
    """
    add_field_date_invoice(cr)
    add_field_invoice_type(cr)
    add_field_invoice_state(cr)
    store_field(cr)


def add_field_date_invoice(cr):
    cr.execute(
        """
        ALTER TABLE account_invoice_line ADD COLUMN IF NOT EXISTS date_invoice date;
        COMMENT ON COLUMN account_invoice_line.date_invoice IS 'Invoice Date';
        """)

def add_field_invoice_type(cr):
    cr.execute(
        """
        ALTER TABLE account_invoice_line ADD COLUMN IF NOT EXISTS invoice_type character varying;
        COMMENT ON COLUMN account_invoice_line.invoice_type IS 'Type';
        """)
    
def add_field_invoice_state(cr):
    cr.execute(
        """
        ALTER TABLE account_invoice_line ADD COLUMN IF NOT EXISTS invoice_state character varying;
        COMMENT ON COLUMN account_invoice_line.invoice_state IS 'Status';
        """)

def store_field(cr):

    _logger.info("Storing computed values of account_invoice_line fields date_invoice, invoice_type, invoice_state")

    if _logger.isEnabledFor(logging.DEBUG):
        start_time = time.time()
    cr.execute(
        """
        UPDATE account_invoice_line line
        SET date_invoice = inv.date_invoice, invoice_type = inv.type, invoice_state = inv.state
        FROM account_invoice AS inv
        WHERE line.invoice_id = inv.id
        """
    )
    if _logger.isEnabledFor(logging.DEBUG):
        end_time = time.time() - start_time
        _logger.debug('%.3fs Stored (account.invoice.line: (date_invoice, invoice_type, invoice_state))' % (end_time))

