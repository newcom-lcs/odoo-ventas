# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
# from odoo.api import Environment, SUPERUSER_ID


class SaleOrderBom(models.Model):
    _name = 'sale.order.bom'
    _description = "Sale BOM"
    _order = 'sequence, id'

    order_id = fields.Many2one('sale.order', 'Sales Order Reference', ondelete='cascade', index=True)

    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True,
        domain=[('sale_ok', '=', True)])
    line_id = fields.Many2one(
        comodel_name='sale.order.line', ondelete='set null', copy=False)
    sequence = fields.Integer(
        string='Sequence', help="Gives the sequence order when displaying a list of optional products.")

    name = fields.Text(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False,
        required=True, precompute=True)

    quantity = fields.Float(
        string="Quantity",
        required=True,
        digits='Product Unit of Measure',
        default=1)
    
    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_uom_id',
        store=True, readonly=False,
        required=True, precompute=True,
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    price_unit = fields.Float(
        string="Product Cost",
        digits='Product Cost',
        )

    is_present = fields.Boolean(
        string="Present on Quotation",
        compute='_compute_is_present',
        search='_search_is_present',
        help="This field will be checked if the option line's product is "
             "already present in the quotation.")

    pending_qty = fields.Float(
        string="Pending Qty",
        compute='_compute_pending_qty',
        store=True, precompute=True, readonly=True
        )

    # add_prefix = fields.Boolean(string="Agregar Prefijo", config_parameter='sale_order.add_bom_prefix')

    #=== COMPUTE METHODS ===#

    @api.depends('product_id')
    def _compute_name(self):
        for option in self:
            if not option.product_id:
                continue
            product_lang = option.product_id.with_context(lang=option.order_id.partner_id.lang)
            option.name = product_lang.get_product_multiline_description_sale()

    @api.depends('product_id')
    def _compute_uom_id(self):
        for option in self:
            if not option.product_id or option.uom_id:
                continue
            option.uom_id = option.product_id.uom_id

    def _get_values_to_add_to_order(self):
        self.ensure_one()
        name = self.name

        add_prefix = self.env['ir.config_parameter'].sudo().get_param('sale_order.add_bom_prefix')

        
        if bool(add_prefix):
            name = "[BOM] " + name
        
        return {
            'order_id': self.order_id.id,
            'price_unit': 0,
            'name': name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.pending_qty,
            'product_uom': self.uom_id.id,
        }

    @api.depends('line_id', 'order_id.order_line', 'product_id')
    def _compute_is_present(self):
        for bom in self:
            bom.is_present = (bom.pending_qty == 0)

    def _search_is_present(self, operator, value):
        if (operator, value) in [('=', True), ('!=', False)]:
            return [('line_id', '=', False)]
        return [('line_id', '!=', False)]

    @api.depends('line_id', 'order_id.order_line', 'product_id')
    def _compute_pending_qty(self):
        for bom in self:
            total = 0
            lista = bom.order_id.order_line.filtered(lambda l: l.product_id == bom.product_id) 

            for i in range(len(lista)):
                total += lista[i].product_uom_qty
            
            bom.pending_qty = bom.quantity - total

        
    #=== ACTION METHODS ===#

    def button_add_to_order(self):
        self.add_option_to_order()

    def add_option_to_order(self):
        self.ensure_one()

        sale_order = self.order_id

        values = self._get_values_to_add_to_order()
        order_line = self.env['sale.order.line'].create(values)

        self.write({'line_id': order_line.id})
        if sale_order:
            sale_order.add_option_to_order_with_taxcloud()




            
