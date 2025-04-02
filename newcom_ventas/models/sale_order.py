from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', domain=[('type', '=', 'opportunity')], store=True)
    business_unit_id = fields.Many2one(
        'business.unit', 
        string='Business Unit',
        related='opportunity_id.business_unit_id',
        store=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        readonly=True
    )
    margen_teorico = fields.Float(string="Margen Teorico (%)", help="Percentage margin to add to the sales order", store=True)
    mes_cierre_facturacion = fields.Date(string="Mes de Cierre (Facturación)", help="Date to generate the invoice", store=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, readonly=True)
    tipo_negocio = fields.Selection([
        ('mantenimiento', 'Mantenimiento'),
        ('cajas', 'Cajas'),
        ('proyectos', 'Proyectos')],
        string="Tipo de Negocio", help="Type of business related to the sales order", store=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, readonly=True)
    state = fields.Selection(selection_add=[('approved', 'Approved')])
    opportunity_count = fields.Integer(string='Opportunity Count', compute='_compute_opportunity_count')

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

    def action_quotation_approve(self):
        """Approve the quotation and move it to approved state."""
        for order in self:
            if order.state == 'sent':
                order.write({'state': 'approved'})
        return True

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