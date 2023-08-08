from odoo import api, fields, models

class sale_order(models.Model):
    _inherit = 'sale.order'
    
    state = fields.Selection(selection_add=[('approved', "Aprobada")])
    
    @api.one
    def action_quotation_approve(self):
        self.state = 'approved'

