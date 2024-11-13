from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    create_analytic_account = fields.Boolean(
        string="Create Analytic Account",
        default=True,
        help="Enable or disable the automatic creation of analytic accounts on sales order confirmation."
    )
