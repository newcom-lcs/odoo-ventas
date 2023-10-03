{
    'name': 'Ventas Newcom',
    'summary': """Módulo con Workflow de Ventas Mejorado""",
    'description': """Funcionalidades
        - Agrega etapa de validación de Orden de Venta
        """,
    'license': 'LGPL-3',
    'author': 'Newcom LCS',
    'category': 'Custom Modules/Workflows',
    'depends': ['base', 'sale_management'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'application': True,
    'installable': True,
}



