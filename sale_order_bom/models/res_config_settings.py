# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    module_sale_order_bom_add_prefix = fields.Boolean("Add [BOM] Prefix to Sale Order")
    

    # @api.onchange('group_sale_order_template')
    # def _onchange_group_sale_order_template(self):
    #     if not self.group_sale_order_template:
    #         self.module_sale_quotation_builder = False

    # def set_values(self):
    #     if not self.group_sale_order_template:
    #         if self.company_so_template_id:
    #             self.company_so_template_id = False
    #         companies = self.env['res.company'].sudo().search([
    #             ('sale_order_template_id', '!=', False)
    #         ])
    #         if companies:
    #             companies.sale_order_template_id = False
    #     super().set_values()
