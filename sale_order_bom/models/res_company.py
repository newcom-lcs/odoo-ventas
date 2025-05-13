from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_hide_bom_items = fields.Boolean(
        string="Ocultar ítems BOM",
        default=False,
        help="Si se activa, se ocultan las líneas de factura cuyo nombre empiece por [BOM]."
    )
    invoice_hide_cero_price = fields.Boolean(
        string="Ocultar ítems con precio cero",
        default=False,
        help="Si se activa, se ocultan las líneas de factura cuyo precio unitario sea cero."
    )

    sale_order_add_bom_prefix = fields.Boolean(
        string="Agregar prefijo [BOM] a materiales de ordendes de venta",
        default=False,
        help="Si se activa, los Items se agegará un prefijo para los items BOM de una Orden de Venta."
    )

