from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # state = fields.Selection(selection_add=[('approved', "Aprobado"), ('sale',)])
    
    # def action_quotation_approve(self):
    #     self.state = 'approved'
    #     return

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        
        # crea una cuenta analítica si no tiene una
        for order in self:
            if not order.analytic_account_id:
                order._create_analytic_account()

    
