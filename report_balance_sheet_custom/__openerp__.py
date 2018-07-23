{
    'name': "Report Balance Sheet Custom",

    'summary': """ """,

    'description': """ This module add new columns in balance sheet printing with comparison and difference
    """,

    'author': "Dedi Sinaga",
    'website': "https://github.com/dedisinaga",
    'category': 'Accounting',
    'version': '8.0.0.1.0',
    'depends': [
        'invoice_supplier_dept_seq',
        'ds_api_analytic_account',
        'report_xlsx',
    ],
    'data': [
        'views/accounting_report_view.xml',
#         'views/account_balance_report_view.xml',
        'report/report_financial.xml',
#         'report/report_trial_balance.xml',
    ],
    'demo': [

    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}