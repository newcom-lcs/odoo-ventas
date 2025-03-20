{
    "name": "Permisos Equipos de Ventas",
    "version": "1.0",
    'license': 'LGPL-3',
    'author': 'Newcom LCS',
    "depends": ["sale_management", "sales_team", "crm", "stock", "purchase", "mail"],
    "summary": "Manage sales orders visibility by team and read-only access to inventory and purchases.",
    "description": """
        - Restrict sales orders visibility based on team membership.
        - Make team_id field read-only for sales orders.
        - Provide read-only access to inventory and purchase data for sales users.
        - Allow sales users to interact with chatter on all documents.
    """,
    "category": "Sales",
    "data": [
        "security/sales_team_security.xml",
        "security/sales_readonly_rules.xml",
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        'views/sale_order_menu.xml',
        'views/res_company.xml',
        'views/sales_readonly_views.xml',
        'views/sale_order_smartbutton_view.xml'
    ],
    "application": False,
    "installable": True,
}
