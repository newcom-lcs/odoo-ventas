from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', store=True)
    business_unit_id = fields.Many2one('business.unit', string='Business Unit', related='opportunity_id.business_unit_id', store=True)
    margen_teorico = fields.Float(string="Margen Teorico (%)", help="Percentage margin to add to the sales order", store=True)
    mes_cierre_facturacion = fields.Date(string="Mes de Cierre (Facturación)", help="Date to generate the invoice", store=True)
    tipo_negocio = fields.Selection([
        ('mantenimiento', 'Mantenimiento'),
        ('cajas', 'Cajas'),
        ('proyectos', 'Proyectos')],
        string="Tipo de Negocio", help="Type of business related to the sales order", store=True)

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