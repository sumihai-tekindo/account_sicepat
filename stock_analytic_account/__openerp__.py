{
    'name': "Stock Analytic Account",
    'summary': """
    This module provides analytic account on stock move
    """,
    'author': "Dedi Sinaga",
    'website': "https://dedisinaga.blogspot.com",
    'category': 'Accounting & Finance',
    'version': '8.0.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'stock',
        'stock_account',
    ],
    'data': [
            'views/stock_analytic_view.xml',
            'views/stock_transfer_view.xml',
            'views/stock_move_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
