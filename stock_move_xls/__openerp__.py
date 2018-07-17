{
    'name': "Stock Move Xls",
    'summary': """
    This module provides analytic account on stock move
    """,
    'author': "Derri Widardi,Aditya Nugraha",
    'website': "",
    'category': 'Accounting & Finance',
    'version': '8.0.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'analytic',
        'report_xls',
    ],
    'data': [
            'wizard/stock_move_views.xml',
            'views/stock_move.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
