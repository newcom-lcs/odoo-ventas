{
    'name': 'Ventas Newcom',
    'summary': """Módulo con Workflow de Ventas Mejorado""",
    'description': """Funcionalidades
        - Agrega etapa de validación de Orden de Venta
        """,
    'licence': 'OPL-1',
    'author': 'Newcom LCS',
    'category': 'Custom Modules/Workflows',
    'depends': ['base', 'sale'],
    'data': [
        'sale_order.xml',
        'sale_order_workflow.xml',
    ],
    'application': True,
    'installable': True,
}



