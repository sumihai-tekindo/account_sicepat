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
	"name": "SICEPAT ACCOUNTING",
	"version": "1.0",
	"depends": [
		"account_accountant",
		'report_xlsx'
		
	],
	"author": "IT Sicepat",
	"category": "SICEPAT ACCOUNTING",
	"description": """ SICEPAT ACCOUNTING :
	
	- Rekapitulasi data customer harus dibuat manual oleh team collection per invoice untuk mendapatkan data AR aging (untuk keperluan penagihan)
	- inherit supplier invoice print
	- tax progresif
	- sales selection
	- Package and Revenue


	""",
	'data': [
             
          'views/saccounting_view.xml',		
          'views/supplier_invoice_action_view2.xml',
          'views/report_supplier_invoice_view2.xml',	
          'sales/sales_inherit_view.xml',
          'wizard/bi_report_wizard.xml',
          'report/report_view.xml',
          ],
	'installable': True,
	'auto_install': False,
	'application': False,
}



