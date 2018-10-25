# -*- coding: utf-8 -*-
##############################################################################
#
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Invoice DownPayment without Purchase Order",
    'summary': """
    This module Invoice DownPayment without Purchase Order
    """,

    'author': "Aditya Nugraha",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'account',
    'version': '8.0.0.1.0',


    # any module necessary for this one to work correctly
		'depends': [
        'account',
    ],

     'data': [
        'views/account_invoice_downpayment.xml',
        'views/account_invoice_advance.xml',
    ],

  
    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
}
