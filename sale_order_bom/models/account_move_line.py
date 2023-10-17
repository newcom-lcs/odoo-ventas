# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'
    
    def isHidden(self):
        hide_bom = self.env['ir.config_parameter'].sudo().get_param('sale_order.invoice_hide_bom_items')
        hide_cero_price = self.env['ir.config_parameter'].sudo().get_param('sale_order.invoice_hide_cero_price')

        if hide_cero_price and self.price_unit == 0:
            return True

        if hide_bom and self.name[:5] == "[BOM]":
            return True
        
        return False


