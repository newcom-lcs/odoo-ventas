{
    'name': 'Invoice Hide Items',
    'summary': """Oculta items con valor 0 en las facturas a cliente""",
    'description': """""",
    'license': 'LGPL-3',
    'author': 'Newcom LCS',
    'category': 'Sales',
    'depends': ['base', 'sale_management'],
    'data': [
        'views/report_invoice.xml',
        # 'security/ir.model.access.csv',
        # 'security/sale_management_security.xml'
    ],
    'application': True,
    'installable': True,
    # 'auto_install': False,
}



