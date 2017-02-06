# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (C) 2016 Dedi Sinaga (<http://dedisinaga.blogspot.com>).
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
    'name': "Stock Receipt",
    'summary': """
    This module add Stock Receipt for Branch
    """,

    'author': "Timotius Wigianto",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '8.0.0.1.0',

    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'stock',
        'base',
        'stock_analytic_account',
        'analytic',
        "hr",
        "mail",
    ],

    # always loaded
    'data': [
        'data/stock_transfer_mail_template.xml',
        'views/stock_receipt_view.xml',
        'views/account_analytic_view.xml',
    ],

    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
}
