{
    'name': 'Sale Order B.O.M',
    'summary': """Lista de Materiales para Ordenes de Venta""",
    'description': """""",
    'license': 'LGPL-3',
    'author': 'Newcom LCS',
    'category': 'Sales',
    'depends': ['base', 'sale_management', 'analytic'],
    'data': [
        'views/sale_order_views.xml',
        'security/ir.model.access.csv',
        'security/sale_management_security.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}



