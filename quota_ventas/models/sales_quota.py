from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class SalesQuota(models.Model):
    _name = 'sales.quota'
    _description = 'Sales Quota'
    _order = 'year desc, quarter desc, team_id, user_id, company_id'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    team_id = fields.Many2one('crm.team', string='Sales Team', required=True)
    user_id = fields.Many2one('res.users', string='Salesperson', required=True)
    year = fields.Char(string=_('Year'), required=True, default=lambda self: str(fields.Date.today().year))
    quarter = fields.Selection([
        ('1', _('Q1')),
        ('2', _('Q2')),
        ('3', _('Q3')),
        ('4', _('Q4'))
    ], string=_('Quarter'), required=True)
    
    currency_id = fields.Many2one(
        'res.currency',
        string=_('Currency'),
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )
    ars_currency_id = fields.Many2one(
        'res.currency',
        string=_('ARS Currency'),
        default=lambda self: self.env.ref('base.ARS').id
    )
    usd_currency_id = fields.Many2one(
        'res.currency',
        string=_('USD Currency'),
        default=lambda self: self.env.ref('base.USD').id
    )
    target_amount = fields.Monetary(
        string=_('Target Amount'),
        required=True,
        currency_field='currency_id'
    )
    achieved_amount = fields.Monetary(
        string=_('Achieved Amount'),
        compute='_compute_achieved_amount',
        store=True,
        currency_field='currency_id'
    )
    total_invoiced_amount = fields.Monetary(
        string=_('Total Invoiced'),
        compute='_compute_total_invoiced',
        store=True,
        currency_field='currency_id',
        help=_('Total amount of all invoices in the period')
    )
    total_invoiced_ars = fields.Monetary(
        string=_('Total Invoiced (ARS)'),
        compute='_compute_total_invoiced',
        store=True,
        currency_field='ars_currency_id',
        help=_('Total amount of all invoices in ARS for the period')
    )
    total_invoiced_usd = fields.Monetary(
        string=_('Total Invoiced (USD)'),
        compute='_compute_total_invoiced',
        store=True,
        currency_field='usd_currency_id',
        help=_('Total amount of all invoices in USD for the period')
    )
    state = fields.Selection([
        ('draft', _('Draft')),
        ('confirmed', _('Confirmed')),
        ('done', _('Done'))
    ], string=_('Status'), default='draft', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string=_('Company'),
        required=True,
        default=lambda self: self.env.company.id
    )

    _sql_constraints = [
        ('unique_quota_period', 'unique(team_id, user_id, year, quarter, company_id)',
         _('A quota already exists for this salesperson in this period and company!'))
    ]

    @api.depends('team_id', 'user_id', 'year', 'quarter')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.team_id.name} - {record.user_id.name} - {record.year} Q{record.quarter}"

    @api.depends('team_id', 'user_id', 'year', 'quarter', 'currency_id')
    def _compute_total_invoiced(self):
        for record in self:
            try:
                # Get the date range for the quarter
                year = int(record.year)
                quarter = int(record.quarter)
                
                # Calculate start and end dates for the quarter
                if quarter == 1:
                    start_date = fields.Date.to_date(f"{year}-01-01")
                    end_date = fields.Date.to_date(f"{year}-03-31")
                elif quarter == 2:
                    start_date = fields.Date.to_date(f"{year}-04-01")
                    end_date = fields.Date.to_date(f"{year}-06-30")
                elif quarter == 3:
                    start_date = fields.Date.to_date(f"{year}-07-01")
                    end_date = fields.Date.to_date(f"{year}-09-30")
                else:  # quarter == 4
                    start_date = fields.Date.to_date(f"{year}-10-01")
                    end_date = fields.Date.to_date(f"{year}-12-31")

                _logger.info('Computing total invoiced for quota %s:', record.name)
                _logger.info('Period: %s to %s', start_date, end_date)
                _logger.info('Team: %s, User: %s', record.team_id.name, record.user_id.name)

                # Search for account moves in the period
                domain = [
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', '=', 'posted'),
                    ('invoice_date', '>=', start_date),
                    ('invoice_date', '<=', end_date),
                    ('team_id', '=', record.team_id.id),
                    ('invoice_user_id', '=', record.user_id.id),
                    ('company_id', '=', record.company_id.id),
                ]

                moves = self.env['account.move'].search(domain)
                _logger.info('Found %d moves matching criteria', len(moves))

                # Initialize amounts
                total_ars = 0.0
                total_usd = 0.0
                
                # Calculate totals for both currencies
                for move in moves:
                    _logger.info('Move: %s', move.name)
                    _logger.info('- Date: %s', move.invoice_date)
                    _logger.info('- Amount ARS: %s', move.amount_untaxed_signed)
                    _logger.info('- Amount USD: %s', move.amount_untaxed_signed_second_currency)
                    _logger.info('- Team: %s', move.team_id.name)
                    _logger.info('- User: %s', move.invoice_user_id.name)
                    
                    total_ars += move.amount_untaxed_signed
                    total_usd += move.amount_untaxed_signed_second_currency

                _logger.info('Final totals:')
                _logger.info('- Total ARS: %s', total_ars)
                _logger.info('- Total USD: %s', total_usd)

                # Set the values
                record.total_invoiced_ars = total_ars
                record.total_invoiced_usd = total_usd
                
                # Set the total in the quota's currency
                if record.currency_id == self.env.ref('base.ARS'):
                    record.total_invoiced_amount = total_ars
                else:
                    record.total_invoiced_amount = total_usd

                _logger.info('Set total_invoiced_amount to: %s', record.total_invoiced_amount)

            except (ValueError, TypeError) as e:
                _logger.error('Error computing total invoiced for quota %s: %s', record.name, str(e))
                record.total_invoiced_amount = 0.0
                record.total_invoiced_ars = 0.0
                record.total_invoiced_usd = 0.0

    @api.depends('team_id', 'user_id', 'year', 'quarter', 'currency_id')
    def _compute_achieved_amount(self):
        for record in self:
            try:
                # Get the date range for the quarter
                year = int(record.year)
                quarter = int(record.quarter)
                
                # Calculate start and end dates for the quarter
                if quarter == 1:
                    start_date = fields.Date.to_date(f"{year}-01-01")
                    end_date = fields.Date.to_date(f"{year}-03-31")
                elif quarter == 2:
                    start_date = fields.Date.to_date(f"{year}-04-01")
                    end_date = fields.Date.to_date(f"{year}-06-30")
                elif quarter == 3:
                    start_date = fields.Date.to_date(f"{year}-07-01")
                    end_date = fields.Date.to_date(f"{year}-09-30")
                else:  # quarter == 4
                    start_date = fields.Date.to_date(f"{year}-10-01")
                    end_date = fields.Date.to_date(f"{year}-12-31")

                # Search for account moves in the period
                domain = [
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', '=', 'posted'),
                    ('invoice_date', '>=', start_date),
                    ('invoice_date', '<=', end_date),
                    ('team_id', '=', record.team_id.id),
                    ('invoice_user_id', '=', record.user_id.id),
                    ('company_id', '=', record.company_id.id),
                ]

                moves = self.env['account.move'].search(domain)
                
                # Calculate the achieved amount based on currency
                achieved_amount = 0.0
                ars_currency = self.env.ref('base.ARS')
                
                for move in moves:
                    if record.currency_id == ars_currency:
                        # For ARS, use amount_untaxed_signed
                        achieved_amount += move.amount_untaxed_signed
                    else:
                        # For USD, use amount_untaxed_signed_second_currency
                        achieved_amount += move.amount_untaxed_signed_second_currency

                record.achieved_amount = achieved_amount
            except (ValueError, TypeError):
                # If there's any error in date conversion or calculation, set to 0
                record.achieved_amount = 0.0

    @api.constrains('year')
    def _check_valid_year(self):
        current_year = fields.Date.today().year
        for record in self:
            try:
                year = int(record.year)
                if year < 2000 or year > current_year + 5:
                    raise ValidationError(_('Please enter a valid year between 2000 and %s') % (current_year + 5))
            except ValueError:
                raise ValidationError(_('Please enter a valid year'))

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_draft(self):
        # Only allow account managers to reset to draft from confirmed or done
        if any(record.state in ['confirmed', 'done'] for record in self):
            if not self.env.user.has_group('account.group_account_manager'):
                raise AccessError(_('Only Account Managers can reset a quota to draft from confirmed or done.'))
        self.write({'state': 'draft'}) 