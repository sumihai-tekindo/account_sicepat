

{
    'name': "Purchase Order Contact vendor",
    'summary': """
    Purchase Order Contact vendor
    """,

    'author': "Aditya Nugraha",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Purchase',
    'version': '8.0.0.1.0',

    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
		'depends': [
        'purchase',
    ],

    # always loaded
    'data': [
        'views/purchase_order.xml',
    ],

    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
}
