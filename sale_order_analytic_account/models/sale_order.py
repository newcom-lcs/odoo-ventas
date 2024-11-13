from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        # crea una cuenta analítica si no tiene una
        for order in self:
            if not order.analytic_account_id and order.company_id.create_analytic_account:
                order._create_analytic_account()
                    
        return result

    