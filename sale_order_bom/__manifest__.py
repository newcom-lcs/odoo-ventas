{
    'name': 'Sale BOM',
    'summary': """Lista de Materiales para Ordenes de Venta""",
    'description': """""",
    'license': 'LGPL-3',
    'author': 'Newcom LCS',
    'category': 'Sales',
    'depends': ['base', 'sale_management'],
    'data': [
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_invoice.xml',
        'security/ir.model.access.csv',
        'security/sale_management_security.xml'
    ],
    'application': True,
    'installable': True,
    # 'auto_install': False,
}



