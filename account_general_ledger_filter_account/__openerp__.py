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

{
    'name': 'Add filter by account to General Ledger report',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'Pambudi Satria',
    'website': 'https://github.com/sumihai-tekindo',
    'description': """

    This module add filter by account to General Ledger report
    ToDo: also modified for pdf

    """,
    'depends': [
        'invoice_supplier_dept_seq',
        'ds_api_analytic_account',
        'report_xlsx',
    ],
    'demo': [],
    'data': [
        'wizard/account_report_general_ledger_view.xml',
    ],
    'active': False,
    'installable': True,
}
