from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        """Override to add notification logic when transfer is validated."""
        _logger.info("Iniciando _action_done para validación de transferencias")
        result = super()._action_done()
        
        # Check if notifications are enabled
        notifications_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'inventory_notifications.enable_notifications', 'True'
        ) == 'True'
        
        if not notifications_enabled:
            _logger.info("Las notificaciones de inventario están deshabilitadas en la configuración")
            return result
        
        for picking in self:
            _logger.info(
                "Procesando transferencia %s - Tipo: %s, Estado: %s, Ubicación: %s",
                picking.name,
                picking.picking_type_id.code,
                picking.state,
                picking.location_dest_id.name
            )
            
            # Send notification for any validated transfer with a related sales order
            if picking.state == 'done' and picking.sale_id:
                _logger.info(
                    "Transferencia %s cumple criterios para notificación. "
                    "Iniciando envío de notificaciones...",
                    picking.name
                )
                self._send_validation_notifications(picking)
            else:
                _logger.info(
                    "Transferencia %s no cumple los criterios para notificación: "
                    "estado=%s, orden de venta asociada=%s",
                    picking.name,
                    picking.state,
                    bool(picking.sale_id)
                )
        
        return result

    def _send_validation_notifications(self, picking):
        """Send notifications when a transfer is validated."""
        try:
            # Get the related sale order
            sale_order = picking.sale_id
            if not sale_order:
                _logger.info(
                    "Transferencia %s no tiene orden de venta asociada. "
                    "No se enviarán notificaciones.",
                    picking.name
                )
                return

            # Get the salesperson
            salesperson = sale_order.user_id
            if not salesperson:
                _logger.info(
                    "Orden de venta %s no tiene vendedor asignado. "
                    "No se enviarán notificaciones.",
                    sale_order.name
                )
                return

            # Create notification content
            note_content = _(
                "La transferencia de stock %s ha sido validada en la ubicación %s. "
                "Validado por: %s\n\n"
                "Detalles de la transferencia:\n"
                "- Referencia: %s\n"
                "- Fecha: %s\n"
                "- Orden de venta: %s\n"
                "- Ubicación destino: %s"
            ) % (
                picking.name,
                picking.location_dest_id.name,
                self.env.user.name,
                picking.name,
                picking.date_done,
                sale_order.name,
                picking.location_dest_id.name
            )

            # Add note to stock picking
            picking.message_post(
                body=note_content,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                author_id=self.env.user.partner_id.id,
                partner_ids=[salesperson.partner_id.id],
            )
            _logger.info("Nota agregada a la transferencia %s", picking.name)

            # Add note to sale order
            sale_order.message_post(
                body=note_content,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                author_id=self.env.user.partner_id.id,
                partner_ids=[salesperson.partner_id.id],
            )
            _logger.info("Nota agregada a la orden de venta %s", sale_order.name)

            # Send email notification
            template = self.env.ref('inventory_notifications.email_template_stock_validation')
            template.send_mail(
                picking.id,
                force_send=True,
                email_values={'email_to': salesperson.email}
            )
            _logger.info("Email enviado al vendedor %s", salesperson.name)

            _logger.info(
                "Todas las notificaciones enviadas exitosamente para la transferencia %s",
                picking.name
            )

        except Exception as e:
            _logger.error(
                "Error al enviar notificaciones para la transferencia %s: %s",
                picking.name,
                str(e)
            )
            raise UserError(_("Error al enviar notificaciones: %s") % str(e)) 