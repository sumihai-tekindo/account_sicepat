{
    'name': "Gross Sale Xls",
    'summary': """
    This module provides analytic account on stock move
    """,
    'author': "Derri Widardi",
    'website': "",
    'category': 'Accounting & Finance',
    'version': '8.0.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'report_xls',
    ],
    'data': [
            'wizard/gross_sale_views_wiz.xml',
            'views/gross_sale.xml',
            'reports/gross_sale.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
