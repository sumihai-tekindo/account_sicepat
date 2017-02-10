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
    'name': 'Customer Churn Report',
    'version': '8.0.1.0.0',
    'category': 'Sales Management',
    'author': 'Pambudi Satria',
    'website': 'https://github.com/sumihai-tekindo',
    'depends': [
        'sale',
    ],
    'data': [
        'views/res_config_views.xml',
        'views/res_company.xml',
        'views/customer_churn_wizard_view.xml',
    ],
    "installable": True,
}
