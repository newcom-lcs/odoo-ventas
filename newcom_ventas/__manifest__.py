{
    'name': 'Custom Sales Order and Partner Fields',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds custom fields to sales orders and partners',
    'description': """
        This module adds the following custom fields:
        - Margen Teorico (Sales Order)
        - Mes de Cierre (Facturacion) (Sales Order)
        - Tipo de Negocio (Sales Order)
        - Cuenta Nueva (Partner)
    """,
    'depends': ['sale', 'base', 'crm', 'sale_management', 'analytic'],
    'data': [
        'views/res_partner_views.xml',
        'views/business_unit_views.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/res_company_views.xml', 
        'views/sale_order_views.xml', 
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
