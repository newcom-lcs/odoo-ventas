from odoo import models, fields, api
from collections import defaultdict

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        """Override to add notification when stock move is done"""
        res = super()._action_done(cancel_backorder=cancel_backorder)
        
        # Group moves by picking and find related orders
        moves_by_picking = defaultdict(list)
        for move in self:
            # Skip if no picking
            if not move.picking_id:
                continue
                
            # Skip if no quantity was actually done
            if not move.quantity_done:
                continue
                
            # Try to find related orders through origin
            sale_order = False
            purchase_order = False
            
            if move.origin:
                # Check for purchase order (starts with P)
                if move.origin.startswith('P'):
                    purchase_order = self.env['purchase.order'].search([('name', 'in', move.origin.split(','))], limit=1)
                # Check for sale order
                else:
                    sale_order = self.env['sale.order'].search([('name', 'in', move.origin.split(','))], limit=1)
            
            if sale_order:
                key = ('sale', move.picking_id, sale_order)
                moves_by_picking[key].append(move)
            elif purchase_order:
                key = ('purchase', move.picking_id, purchase_order)
                moves_by_picking[key].append(move)
        
        # Create and send notifications for each picking/order combination
        for (order_type, picking, order), moves in moves_by_picking.items():
            # Get operation type name
            operation_name = picking.picking_type_id.name if picking.picking_type_id else 'N/A'
            
            if order_type == 'sale':
                # Handle sales order notification
                salesperson_name = order.user_id.name if order.user_id else ""
                project_responsible_name = order.project_responsible_id.name if order.project_responsible_id else ""
                message = self._create_sale_notification_message(picking, moves, operation_name, salesperson_name, project_responsible_name)
                subject = f"Actualización de Pedido {order.name} - {operation_name}"
                # Include both salesperson and project responsible in notifications
                partner_ids = []
                if order.user_id and order.user_id.partner_id:
                    partner_ids.append(order.user_id.partner_id.id)
                if order.project_responsible_id and order.project_responsible_id.partner_id:
                    partner_ids.append(order.project_responsible_id.partner_id.id)
            else:
                # Handle purchase order notification
                user_name = order.user_id.name if order.user_id else ""
                message = self._create_purchase_notification_message(picking, moves, operation_name, user_name)
                subject = f"Actualización de Orden de Compra {order.name} - {operation_name}"
                partner_ids = [order.user_id.partner_id.id] if order.user_id and order.user_id.partner_id else []
            
            # Post message to the order and notify the users
            order.message_post(
                body=message,
                subject=subject,
                message_type='comment',
                subtype_xmlid='mail.mt_note',
                partner_ids=partner_ids,
                is_internal=True
            )
            
        return res

    def _create_sale_notification_message(self, picking, moves, operation_name, salesperson_name, project_responsible_name):
        """Create notification message for sales orders"""
        # Convert server time to user timezone
        user_time = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        
        # Create greeting based on who is being notified
        if salesperson_name and project_responsible_name:
            greeting = f"Hola {salesperson_name} y {project_responsible_name}"
        elif salesperson_name:
            greeting = f"Hola {salesperson_name}"
        elif project_responsible_name:
            greeting = f"Hola {project_responsible_name}"
        else:
            greeting = "Hola"
            
        message = f"""
        <div style="margin: 0px; padding: 0px;">
            <p style="margin: 0px; padding: 0px; font-size: 13px;">
                {greeting}, se ha completado la siguiente operación en el depósito:<br/>
                <br/>
                <strong>{operation_name}</strong><br/>
                • Origen: {moves[0].location_id.name}<br/>
                • Destino: {moves[0].location_dest_id.name}<br/>
                • Referencia: {picking.name}<br/>
                • Validado por: {self.env.user.name}<br/>
                • Fecha: {user_time}<br/>
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
        
        return message

    def _create_purchase_notification_message(self, picking, moves, operation_name, user_name):
        """Create notification message for purchase orders"""
        # Convert server time to user timezone
        user_time = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        message = f"""
        <div style="margin: 0px; padding: 0px;">
            <p style="margin: 0px; padding: 0px; font-size: 13px;">
                Hola {user_name}, se ha completado la siguiente operación en el depósito:<br/>
                <br/>
                <strong>{operation_name}</strong><br/>
                • Origen: {moves[0].location_id.name}<br/>
                • Destino: {moves[0].location_dest_id.name}<br/>
                • Referencia: {picking.name}<br/>
                • Validado por: {self.env.user.name}<br/>
                • Fecha: {user_time}<br/>
                <br/>
                <strong>Productos procesados:</strong><br/>
        """
        
        # Add details for each product
        for move in moves:
            message += f"• {move.product_id.name}: {move.quantity_done} {move.product_uom.name}<br/>"
        
        message += """
            </p>
        </div>
        """
        
        return message 