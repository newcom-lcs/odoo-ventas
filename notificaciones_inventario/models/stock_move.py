from odoo import models, fields, api
from collections import defaultdict

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        """Override to add notification when stock move is done"""
        res = super()._action_done(cancel_backorder=cancel_backorder)
        
        # Skip if this is a receipt from supplier (first stage)
        if self.mapped('location_id.usage') == ['supplier']:
            return res
            
        # Group moves by picking and find related sale orders
        moves_by_picking = defaultdict(list)
        for move in self:
            # Skip if no picking
            if not move.picking_id:
                continue
                
            # Skip if no quantity was actually done
            if not move.quantity_done:
                continue
                
            # Try to find related sale order through origin
            sale_order = False
            if move.origin:
                sale_order = self.env['sale.order'].search([('name', 'in', move.origin.split(','))], limit=1)
            
            if sale_order:
                key = (move.picking_id, sale_order)
                moves_by_picking[key].append(move)
        
        # Create and send one notification per picking/order combination
        for (picking, order), moves in moves_by_picking.items():
            # Get operation type name
            operation_name = picking.picking_type_id.name if picking.picking_type_id else 'N/A'
            
            # Get salesperson name without @ symbol
            salesperson_name = order.user_id.name if order.user_id else ""
            
            # Create detailed notification message with HTML formatting
            message = f"""
            <div style="margin: 0px; padding: 0px;">
                <p style="margin: 0px; padding: 0px; font-size: 13px;">
                    Hola {salesperson_name}, se ha completado la siguiente operación en el depósito:<br/>
                    <br/>
                    <strong>{operation_name}</strong><br/>
                    • Origen: {moves[0].location_id.name}<br/>
                    • Destino: {moves[0].location_dest_id.name}<br/>
                    • Referencia: {picking.name}<br/>
                    • Validado por: {self.env.user.name}<br/>
                    • Fecha: {fields.Datetime.now()}<br/>
                    <br/>
                    <strong>Productos procesados:</strong><br/>
            """
            
            # Add details for each product
            for move in moves:
                message += f"• {move.product_id.name}: {move.quantity_done} {move.product_uom.name}<br/>"
            
            # Only add delivery time message for outgoing shipments
            if picking.picking_type_id.code == 'outgoing':
                message += """
                    <br/>
                    <strong>La entrega al cliente puede tardar hasta 72 horas. Por favor, esperar este tiempo antes de enviar la factura al cliente.</strong>
                </p>
            </div>
            """
            else:
                message += """
                </p>
            </div>
            """
            
            # Create subject for the notification
            subject = f"Actualización de Pedido {order.name} - {operation_name}"
            
            # Post message to the sale order and notify the salesperson
            order.message_post(
                body=message,
                subject=subject,
                message_type='comment',
                subtype_xmlid='mail.mt_note',
                partner_ids=[order.user_id.partner_id.id] if order.user_id and order.user_id.partner_id else [],
                is_internal=True
            )
            
        return res 