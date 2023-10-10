# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bom = fields.Boolean("Material Adicional", default=False)

    
    
        # Fields specifying custom line logic
    # display_type = fields.Selection(
    #     selection=[
    #         ('line_section', "Section"),
    #         ('line_note', "Note"),
    #     ],
    #     default=False)

