{
    'name': 'Sales Quota Management',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage sales quotas for sales teams and salespeople',
    'description': """
        This module allows you to:
        * Define sales quotas for each salesperson
        * Set quarterly targets
        * Track sales team performance
    """,
    'author': 'Newcom',
    'website': 'https://www.newcom.cl',
    'depends': ['base', 'sales_team', 'multicurrency_journal_items', 'crm', 'permisos_equipos_ventas'],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_quota_views.xml',
        'views/crm_team_inherit_sales_quota.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
} 