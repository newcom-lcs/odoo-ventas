from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    use_approval_flow = fields.Boolean(
        string="Usar Flujo de Aprobación",
        help="Marque esta casilla para habilitar el flujo de aprobaciones en la compañía.",
        default=False
    )
