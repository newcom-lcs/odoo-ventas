from odoo import fields, models, api

class InventoryConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_inventory_notifications = fields.Boolean(
        string='Habilitar Notificaciones de Inventario',
        config_parameter='inventory_notifications.enable_notifications',
        default=True,
        help='Habilitar notificaciones para todos los movimientos de inventario relacionados con órdenes de venta'
    )

    @api.model
    def get_values(self):
        res = super(InventoryConfigSettings, self).get_values()
        res.update(
            enable_inventory_notifications=self.env['ir.config_parameter'].sudo().get_param(
                'inventory_notifications.enable_notifications', 'True'
            ) == 'True'
        )
        return res

    def set_values(self):
        super(InventoryConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'inventory_notifications.enable_notifications',
            str(self.enable_inventory_notifications)
        ) 