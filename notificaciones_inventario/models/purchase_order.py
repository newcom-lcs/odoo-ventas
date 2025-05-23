from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        """Override to set the current user as the buyer when confirming the order"""
        # Set the current user as the buyer before confirming
        self.write({'user_id': self.env.user.id})
        return super().button_confirm() 