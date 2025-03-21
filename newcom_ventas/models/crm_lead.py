from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    business_unit_id = fields.Many2one(
        'business.unit',
        string='Business Unit',
        store=True
    ) 