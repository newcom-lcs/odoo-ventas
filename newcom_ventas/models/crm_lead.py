from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    business_unit_id = fields.Many2one(
        'business.unit',
        string='Business Unit',
        store=True
    )

    @api.constrains('business_unit_id', 'probability')
    def _check_business_unit_change(self):
        for record in self:
            if record.probability in [0, 100] and 'business_unit_id' in record._get_modified_fields():
                raise ValidationError('Business Unit cannot be modified when opportunity is won or lost.')

    @api.depends('probability')
    def _compute_business_unit_readonly(self):
        for record in self:
            record.business_unit_readonly = record.probability in [0, 100]

    business_unit_readonly = fields.Boolean(
        compute='_compute_business_unit_readonly',
        store=True
    )

    @api.onchange('business_unit_readonly')
    def _onchange_business_unit_readonly(self):
        if self.business_unit_readonly:
            self.business_unit_id.readonly = True 