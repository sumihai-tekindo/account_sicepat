 # -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Trihatmoko (<http://sicepat.com>).
#    @author Trihatmoko <indardin@sicepat.com>
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
	"name": "BUSINESS INTELLENGENCE",
	"version": "1.0",
	"depends": [
		"account_accountant",
		'report_xlsx'
		
	],
	"author": "IT Sicepat",
	"category": "BUSINESS INTELLENGENCE",
	"description": """ BUSINESS INTELLENGENCE :
	
	- sales revenue
	- Package and Revenue
	- Revenue per lokasi
	- Report BI


	""",
	'external dependencies': {'python': ['pymssql']},
	'data': [
             
          'sales/sales_inherit_view.xml',
          'sales/bi_view.xml',
          'wizard/bi_report_wizard.xml',
          'wizard/pendapatan_wizard.xml',

          'security/ir.module.category.csv',
          'security/res.groups.csv',
          'security/ir.model.access.csv',
         ],
    'qweb': [
        'static/src/xml/lib.xml',
    ],
	'installable': True,
	'auto_install': False,
	'application': False,
}



