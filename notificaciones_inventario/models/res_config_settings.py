from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_inventory_notifications = fields.Boolean(
        string='Habilitar Notificaciones de Inventario',
        config_parameter='inventory_notifications.enable_notifications',
        default=True,
        help='Habilitar notificaciones para todos los movimientos de inventario relacionados con órdenes de venta'
    ) 