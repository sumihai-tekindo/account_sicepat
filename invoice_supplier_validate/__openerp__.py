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
    'name': "Validation on Supplier Invoices",

    'summary': """
        Validation on Supplier Invoices
    """,

    'description': """
===============================
Validation on Supplier Invoices
===============================


    """,

    'author': "Pambudi Satria",
    'website': "https://github.com/sumihai-tekindo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '8.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'purchase',
        'purchase_requisition',
    ],

    # always loaded
    'data': [
        'security/account_security.xml',
        'views/account_invoice_view.xml',
        'views/account_invoice_workflow.xml',
        'wizard/account_invoice_state.xml',
        'views/purchase_order_view.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
}