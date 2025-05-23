# Notificaciones de Movimientos de Stock

Un módulo de Odoo que notifica las órdenes de venta y compra cuando se completan los movimientos de stock relacionados.

## Características
- Notificaciones automáticas en órdenes de venta cuando se completan movimientos de stock
- Notificaciones automáticas en órdenes de compra cuando se reciben mercancías
- Muestra el nombre del producto y la cantidad en las notificaciones
- Notifica al vendedor asignado en órdenes de venta
- Notifica al comprador asignado en órdenes de compra

## Instalación
1. Instale el módulo en su instancia de Odoo
2. No requiere configuración - funciona automáticamente

## Uso
- Cuando complete un movimiento de stock que esté relacionado con una orden de venta, aparecerá automáticamente una notificación en el chatter de la orden de venta
- Cuando complete un movimiento de stock que esté relacionado con una orden de compra (referencia que comienza con 'P'), aparecerá automáticamente una notificación en el chatter de la orden de compra
- Las notificaciones incluyen detalles como la ubicación de origen, destino, productos procesados y quién realizó la validación 