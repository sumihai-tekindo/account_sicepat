
{
    'name': 'Customer Classification',
    'version': '8.0.1.0.0',
    'category': 'Sale',
    'author': 'Dedi Sinaga',
    'website': 'https://github.com/githubsicepat',
    'depends': [
        'base','sale','account','materialized_sql_view','invoice_supplier_dept_seq'
    ],
    'data': [
        'datas/sequence.xml',
        'materialized_views/revenue_materialized_view.xml',
        'views/customer_grade_view.xml',
        'views/res_partner_view.xml',
        'views/customer_invoice_view.xml',
        'views/account_move.xml',
    ],
    "installable": True,
}
