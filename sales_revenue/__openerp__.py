

{
	"name": "SALES REVENUE REPORT",
	"version": "1.0",
	"depends": [
		"account_accountant",
		'report_xlsx'
		
	],
	"author": "",
	"category": "Sales Revenue Report",
	"description": """ Sales Revenue Report :
	
	- sales revenue
	- Package and Revenue
	- Revenue per lokasi
	- Report BI


	""",
	'external dependencies': {'python': ['pymssql']},
	'data': [
             
          'views/sales_revenue_view.xml',

         ],
    'qweb': [
        'static/src/xml/lib.xml',
    ],
	'installable': True,
	'auto_install': False,
	'application': False,
}



