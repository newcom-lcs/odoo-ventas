from odoo import models, fields, api
from datetime import datetime, timedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Field to store the original creation date for importing
    original_creation_date = fields.Date(string="Original Creation Date")

    cuenta_nueva = fields.Boolean(string="Cuenta Nueva", compute='_compute_cuenta_nueva', store=True)

    @api.depends('create_date')
    def _compute_cuenta_nueva(self):
        for record in self:
            if record.create_date:
                # Calculate the end of the 365-day period after `create_date`
                expiration_date = record.create_date + timedelta(days=365)

                # Set `cuenta_nueva` to True if today is within the first 365 days; otherwise, False
                record.cuenta_nueva = record.create_date <= datetime.now() <= expiration_date
            else:
                record.cuenta_nueva = False  # Default to False if `create_date` is not set

    @api.model
    def update_creation_date_from_original(self):
        # Find partners with an `original_creation_date` set
        partners_to_update = self.search([('original_creation_date', '!=', False)])

        # Step 1: Update `create_date` using SQL, setting time to UTC midnight
        for partner in partners_to_update:
            # Set `original_creation_date` as a datetime at midnight UTC
            creation_datetime_utc = fields.Datetime.to_string(
                fields.Datetime.from_string(str(partner.original_creation_date) + ' 00:00:00')
            )

            # Direct SQL update for `create_date` in UTC midnight
            self.env.cr.execute(
                """
                UPDATE res_partner
                SET create_date = %s
                WHERE id = %s
                """,
                (creation_datetime_utc, partner.id)
            )

        # Step 2: Commit the changes to save them in the database
        self.env.cr.commit()

        # Step 3: Calculate and update `cuenta_nueva` after committing
        for partner in partners_to_update:
            # Fetch the latest `create_date` after the commit
            if partner.create_date:
                expiration_date = partner.create_date + timedelta(days=365)
                # Set `cuenta_nueva` to True if today is within the first 365 days; otherwise, False
                partner.cuenta_nueva = datetime.now() <= expiration_date
            else:
                partner.cuenta_nueva = False