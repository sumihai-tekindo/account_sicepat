{
    'name': "Asset Analytic Modification",

    'summary': """
    """,

    'author': "Dedi Sinaga",
    'website': "https://dedisinaga.blogspot.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
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
        'views/account_asset_view.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
}
