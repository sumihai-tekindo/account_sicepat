{
    'name': "Quantity Can't More Than Purchase Order & Supplier Invoice",
    'summary': """
    check qty receipt and purchase order & Supplier Invoice
    """,
    'author': "Aditya Nugraha",
    'website': "",
    'category': 'Purchase',
    'version': '8.0.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'purchase',
        'stock_analytic_account',
        'hr_stock_transfer',
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
}
