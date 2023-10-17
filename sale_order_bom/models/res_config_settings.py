# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_sale_order_bom_add_prefix = fields.Boolean("Add [BOM] Prefix to Sale Order")
    module_sale_order_invoice_hide_bom_items = fields.Boolean("Hide items with '[BOM]' prefix from customer invoices")
    module_sale_order_invoice_hide_items_with_cero_price = fields.Boolean("Hide items with price = 0 from customer invoices")

    def set_values(self):
       res = super(ResConfigSettings, self).set_values()
       self.env['ir.config_parameter'].sudo().set_param('sale_order.add_bom_prefix', self.module_sale_order_bom_add_prefix)
       self.env['ir.config_parameter'].sudo().set_param('sale_order.invoice_hide_bom_items', self.module_sale_order_invoice_hide_bom_items)
       self.env['ir.config_parameter'].sudo().set_param('sale_order.invoice_hide_cero_price', self.module_sale_order_invoice_hide_items_with_cero_price)
       return res
    @api.model
    def get_values(self):
       res = super(ResConfigSettings, self).get_values()
       ICPSudo = self.env['ir.config_parameter'].sudo()
       res.update(
           module_sale_order_bom_add_prefix=ICPSudo.get_param('sale_order.add_bom_prefix'),
           module_sale_order_invoice_hide_bom_items=ICPSudo.get_param('sale_order.invoice_hide_bom_items'),
           module_sale_order_invoice_hide_items_with_cero_price=ICPSudo.get_param('sale_order.invoice_hide_cero_price'),
       )
       return res

