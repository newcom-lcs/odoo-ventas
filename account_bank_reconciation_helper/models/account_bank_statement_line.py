from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext

from odoo.addons.base.models.res_bank import sanitize_account_number

from xmlrpc.client import MAXINT
from itertools import product

import re


class AccountBankStatementLine(models.Model):
    _name = "account.bank.statement.line"
    _inherit = 'account.bank.statement.line'

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            vals['partner_id'] = self._buscar_partner(vals['payment_ref'])

        return super().create(vals_list)
    
    
    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------
    def _buscar_partner(self, payment_ref):

        if self.partner_id:
            return self.partner_id
        
        

        # raise ValidationError(payment_ref)

        if match := re.search(r'[^0-9]([0-9]{11})', payment_ref):
            cuit = match.group(1)
        
            domains = product(
                [
                    ('vat', '=ilike', cuit),
                    ('vat', 'ilike', cuit),
                ],
                [
                    ('company_id', '=', self.company_id.id),
                    ('company_id', '=', False),
                ],
            )
            
            for domain in domains:
                partner = self.env['res.partner'].search(list(domain) + [('parent_id', '=', False)], limit=1)
                if partner:
                    return partner.id

        return self.partner_id




