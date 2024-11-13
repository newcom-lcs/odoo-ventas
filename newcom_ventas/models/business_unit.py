from odoo import models, fields

class BusinessUnit(models.Model):
    _name = 'business.unit'
    _description = 'Business Unit'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    business_unit_id = fields.Many2one('business.unit', string='Business Unit')