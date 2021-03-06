# -*- coding: utf-8 -*-

{
	"name": "Sales Revenue Report",
	"version": "1.0",
	"depends": [
		'materialized_sql_view',
		'account_accountant',
		'sicepat_erp',
	],
	"author": "Pambudi Satria",
	"description": """ Sicepat Sales Revenue Report:
		
		- Revenue Analysis
		- By Services
		- By Location
		- By Store
		- By Partner
		- By Sales
		- Net Revenue
		- New Partner
	""",
	'data': [
		'security/ir.model.access.csv',
		'data/res.store.csv',
		'views/sales_revenue_view.xml',
		'views/store_view.xml',
		'security/sales_revenue_security.xml',
	],
    'qweb': [],
	'installable': True,
	'auto_install': False,
	'application': False,
}
