{
    'name': "Generate Asset Code - Account asset asset",

    'summary': """
    """,

    'author': "Aditya Nugraha",

    # for the full list
    'category': 'Accounting',
    'version': '8.0.0.1.0',

    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'account_asset',
        "analytic",
    ],

    # always loaded
    'data': [
        'views/account_asset_code_view.xml',
        'views/sequence_view.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
}
