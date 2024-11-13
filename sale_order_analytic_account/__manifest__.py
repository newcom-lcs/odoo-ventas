{
    'name': 'Sale Order Analytic Account',
    'summary': """Fuerza creación de cuenta analítica en orden de venta""",
    'description': """""",
    'license': 'LGPL-3',
    'author': 'Newcom LCS',
    'category': 'Sales',
    'depends': ['base', 'sale_management', 'analytic'],
    'data': [
        'views/res_company_views.xml', 
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}



