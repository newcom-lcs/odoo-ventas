from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # state = fields.Selection(selection_add=[('approved', "Aprobado"), ('sale',)])
    
    # def action_quotation_approve(self):
    #     self.state = 'approved'
    #     return

