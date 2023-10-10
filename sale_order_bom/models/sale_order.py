# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import SUPERUSER_ID, api, fields, models, _
from odoo.exceptions import ValidationError

from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_bom_ids = fields.One2many(
        comodel_name='sale.order.bom', inverse_name='order_id',
        string="BOM Products Lines",
        states=READONLY_FIELD_STATES,
        copy=True)

