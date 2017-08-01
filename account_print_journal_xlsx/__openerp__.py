# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 STI (<https://github.com/sumihai-tekindo>).
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
    'name': 'Account Journal XLSX Report',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': "Pambudi Satria",
    'category': 'Accounting & Finance',
    'depends': [
        'account',
        'report_xlsx',
    ],
    'demo': [],
    'data': [
        'views/report_journal_xlsx.xml',
        'wizard/account_report_print_journal_xlsx_view.xml',
    ],
    'test': [
#         'tests/print_journal_by_fiscal_year.yml',
#         'tests/print_journal_by_period.yml',
#         'tests/export_csv_journal_by_fiscal_year.yml',
#         'tests/export_csv_journal_by_period.yml',
    ],
    'installable': True,
}
