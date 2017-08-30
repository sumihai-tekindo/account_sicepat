{
    'name': "Sales Order Analytic",
    'summary': """
    This is the module of Sales Order Analytic
    """,

    'author': "Andrean Wijaya",
    'website': "-",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': '-',
    'version': '8.0.0.1.0',

    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'sale','base',
    ],

    # always loaded
    'data': [
        'views/sales_order_analytic_view.xml',
    ],

    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
}