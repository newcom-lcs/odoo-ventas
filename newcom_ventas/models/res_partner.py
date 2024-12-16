from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Manual boolean field
    cuenta_nueva = fields.Boolean(
        string="Cuenta Nueva",
        help="Es una cuenta nueva?"
    )

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """
        Override fields_get to make the `cuenta_nueva` field readonly 
        for users not in the `base.group_system` group.
        """
        fields = super(ResPartner, self).fields_get(allfields=allfields, attributes=attributes)
        if not self.env.user.has_group('base.group_system'):
            if 'cuenta_nueva' in fields:
                fields['cuenta_nueva']['readonly'] = True
        return fields
