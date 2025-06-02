from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_responsible_id = fields.Many2one(
        'res.users',
        string='Responsable de Proyecto',
        help='Usuario que recibirá las notificaciones de material',
        tracking=True,
        index=True
    ) 