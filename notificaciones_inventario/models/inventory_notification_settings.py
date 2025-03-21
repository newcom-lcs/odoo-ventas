from odoo import fields, models

class InventoryNotificationSettings(models.Model):
    _name = 'inventory.notification.settings'
    _description = 'Configuración de Notificaciones de Inventario'

    name = fields.Char(string='Nombre', required=True, default='Configuración de Notificaciones')
    enable_notifications = fields.Boolean(
        string='Habilitar Notificaciones', 
        default=True,
        help='Enviar notificaciones por cada movimiento de inventario relacionado con órdenes de venta'
    ) 