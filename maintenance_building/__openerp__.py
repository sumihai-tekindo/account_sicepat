
{
    'name': "Building Maintenance",
    'summary': """
     Manage Building Maintenance)
    """,

    'author': "Aditya Nugraha ",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Maintenance Asset',
    'version': '8.0.0.1.0',

    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
	'depends': [
        'product',
        'account',
        'asset',
        'purchase',
    ],

    # always loaded
    'data': [
        # 'views/maintenance_building.xml',
        'views/maintenance.xml',
    ],

    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
}
