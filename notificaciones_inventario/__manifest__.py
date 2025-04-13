{
    'name': 'Stock Move Notifications',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Notify sales orders when stock moves occur',
    'description': """
        This module adds notifications to sales orders when related stock moves are completed.
        It helps sales teams stay informed about inventory movements.
    """,
    'license': 'LGPL-3',
    'author': 'Newcom LCS',
    'depends': ['stock', 'sale'],
    'data': [
        'models/res_config_settings.py',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
} 