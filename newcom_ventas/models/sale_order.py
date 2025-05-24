from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', domain=[('type', '=', 'opportunity')], store=True)
    business_unit_id = fields.Many2one(
        'business.unit', 
        string='Business Unit',
        store=True,
        required=True
    )
    margen_teorico = fields.Float(
        string="Margen Teorico (%)", 
        help="Percentage margin to add to the sales order", 
        store=True
    )
    mes_cierre_facturacion = fields.Date(string="Mes de Cierre (Facturación)", help="Date to generate the invoice", store=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, readonly=True)
    tipo_negocio = fields.Selection([
        ('mantenimiento', 'Mantenimiento'),
        ('cajas', 'Cajas'),
        ('proyectos', 'Proyectos')],
        string="Tipo de Negocio", 
        help="Type of business related to the sales order", 
        store=True,
        required=True
    )
    state = fields.Selection(selection_add=[('approved', 'Approved')])
    opportunity_count = fields.Integer(string='Opportunity Count', compute='_compute_opportunity_count')

    @api.depends('margen_teorico')
    def _compute_margen_teorico_display(self):
        for record in self:
            if self.env.user.has_group('account.group_account_manager'):
                record.margen_teorico_display = record.margen_teorico
            else:
                record.margen_teorico_display = record.margen_teorico

    margen_teorico_display = fields.Float(
        string="Margen Teórico (Editable)",
        compute='_compute_margen_teorico_display',
        inverse='_inverse_margen_teorico_display',
        store=False
    )

    def _inverse_margen_teorico_display(self):
        for record in self:
            if self.env.user.has_group('account.group_account_manager'):
                record.margen_teorico = record.margen_teorico_display

    def write(self, vals):
        """
        Prevent non-accounting managers from modifying margen_teorico.
        """
        if 'margen_teorico' in vals and not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_("No tiene permisos para modificar el campo 'Margen Teórico'."))
        return super(SaleOrder, self).write(vals)

    def _compute_opportunity_count(self):
        for order in self:
            order.opportunity_count = 1 if order.opportunity_id else 0

    def action_view_opportunity(self):
        self.ensure_one()
        if not self.opportunity_id:
            return {}
        
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Opportunity',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'res_id': self.opportunity_id.id,
            'context': {'default_type': 'opportunity'}
        }
        return action

    def _select(self):
        return super(SaleReport, self)._select() + """
            , s.tipo_negocio
            , s.margen_teorico
            , s.business_unit_id
            , s.mes_cierre_facturacion
        """
    
    def _group_by(self):
        return super(SaleReport, self)._group_by() + """
            , s.tipo_negocio
            , s.margen_teorico
            , s.business_unit_id
            , s.mes_cierre_facturacion
        """
        
    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        # crea una cuenta analítica si no tiene una
        for order in self:
            if not order.analytic_account_id and order.company_id.create_analytic_account:
                order._create_analytic_account()
                    
        return result


class SaleReport(models.Model):
    _inherit = "sale.report"

    tipo_negocio = fields.Selection([
        ('mantenimiento', 'Mantenimiento'),
        ('cajas', 'Cajas'),
        ('proyectos', 'Proyectos')],
        string="Tipo de Negocio", readonly=True)
    margen_teorico = fields.Float(string="Margen Teorico (%)", readonly=True)
    business_unit_id = fields.Many2one('business.unit', string='Business Unit', readonly=True)
    mes_cierre_facturacion = fields.Date(string="Mes de Cierre (Facturación)", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['tipo_negocio'] = "s.tipo_negocio"
        res['margen_teorico'] = "s.margen_teorico"
        res['business_unit_id'] = "s.business_unit_id"
        res['mes_cierre_facturacion'] = "s.mes_cierre_facturacion"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.tipo_negocio,
            s.margen_teorico,
            s.business_unit_id,
            s.mes_cierre_facturacion"""
        return res