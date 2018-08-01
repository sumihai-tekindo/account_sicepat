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
    'name': "Code Aset",
    'summary': """
    This module add Code Asset.variant (product_product)
    """,

    'author': "Aditya Nugraha ",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Purchase',
    'version': '8.0.0.1.0',

    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
		'depends': [
        'product',
        'purchase',
    ],

    # always loaded
    'data': [
        'views/code_aset_view.xml',
    ],

    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
}
