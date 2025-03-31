from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError
from datetime import timedelta
import pytz

class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(selection_add=[
        ('manager_approval', 'Aprobación del Gerente'),
        ('cost_approval', 'Aprobación de Costos')
    ], default='draft')

    cost_approval = fields.Boolean(string="Aprobación de Costos", tracking=True)
    manager_approval = fields.Boolean(string="Aprobación del Gerente", tracking=True)

    # Campos para rastrear las fechas de cada transición
    quotation_to_manager_date = fields.Datetime(string="De Cotización a Aprobación del Gerente", readonly=True)
    manager_to_costs_date = fields.Datetime(string="De Aprobación del Gerente a Aprobación de Costos", readonly=True)
    costs_to_confirmed_date = fields.Datetime(string="De Aprobación de Costos a Confirmado", readonly=True)

    manager_approver_id = fields.Many2one('res.users', string='Approved by Manager', readonly=True)
    cost_approver_id = fields.Many2one('res.users', string='Approved by Cost', readonly=True)

    rejection_reason = fields.Text(string="Rejection Reason")

    def _compute_elapsed_time(self, start_date, end_date):
        """
        Calcula el tiempo transcurrido entre dos fechas en días, horas y minutos.
        """
        if start_date and end_date:
            elapsed_time = end_date - start_date
            days = elapsed_time.days
            hours, remainder = divmod(elapsed_time.seconds, 3600)
            minutes = remainder // 60
            return f"{days} días, {hours} horas, {minutes} minutos"
        return "N/A"

    def _get_user_timezone(self):
        """
        Obtiene la zona horaria del usuario actual. Si no está configurada, usa UTC.
        """
        tz_name = self.env.user.tz or 'UTC'
        return pytz.timezone(tz_name)

    def _convert_to_user_timezone(self, utc_datetime):
        """
        Convierte un datetime UTC a la zona horaria del usuario actual.
        """
        if not utc_datetime:
            return None
        user_tz = self._get_user_timezone()
        return pytz.utc.localize(utc_datetime).astimezone(user_tz)

    def action_draft(self):
        """
        Sobrescribe la acción para volver a cotización (draft).
        Restablece los campos de rastreo y agrega un mensaje al chatter.
        """
        for order in self:
            # Reset tracking fields
            order.quotation_to_manager_date = None
            order.manager_to_costs_date = None
            order.costs_to_confirmed_date = None
            order.manager_approval = False
            order.cost_approval = False
            
            # Add a chatter message
            order.message_post(
                body=(
                    "El pedido se ha restablecido a cotización. "
                    "Todos los tiempos de aprobación han sido reiniciados."
                )
            )
        return super(SaleOrder, self).action_draft()

    def action_confirm(self):
        """
        Sobrescribe el botón de confirmación para aplicar el flujo de aprobaciones 
        solo si está habilitado en la compañía. Si no, funciona como el estándar.
        """
        for order in self:
            if not order.company_id.use_approval_flow:
                # Si el flujo está desactivado, usa la lógica estándar de Odoo
                return super(SaleOrder, self).action_confirm()

            valid_transitions = {
                'draft': 'manager_approval',
                'manager_approval': 'cost_approval',
                'cost_approval': 'sale'
            }

            current_state = order.state
            if current_state not in valid_transitions:
                if current_state == 'sale':
                    return True
                raise UserError(f"Invalid state transition from {current_state}")

            next_state = valid_transitions[current_state]

            # Lógica del flujo de aprobaciones
            if current_state == 'draft':
                order.quotation_to_manager_date = fields.Datetime.now()
                local_time = self._convert_to_user_timezone(order.quotation_to_manager_date)
                tz_name = self.env.user.tz or 'UTC'
                elapsed_time = self._compute_elapsed_time(order.create_date, order.quotation_to_manager_date)
                order.message_post(
                    body=(
                        f"La cotización pasó a 'Aprobación del Gerente' el {local_time.strftime('%Y-%m-%d %H:%M:%S')} ({tz_name}) "
                        f"por el usuario: {self.env.user.name}.<br>"
                        f"Tiempo Transcurrido: {elapsed_time}."
                    )
                )
                order.state = next_state

            elif current_state == 'manager_approval':
                if not order.manager_approval:
                    raise UserError("Se requiere la aprobación del gerente para continuar.")
                order.manager_to_costs_date = fields.Datetime.now()
                local_time = self._convert_to_user_timezone(order.manager_to_costs_date)
                tz_name = self.env.user.tz or 'UTC'
                elapsed_time = self._compute_elapsed_time(order.quotation_to_manager_date, order.manager_to_costs_date)
                order.message_post(
                    body=(
                        f"El estado pasó de 'Aprobación del Gerente' a 'Aprobación de Costos' el {local_time.strftime('%Y-%m-%d %H:%M:%S')} ({tz_name}) "
                        f"por el usuario: {self.env.user.name}.<br>"
                        f"Tiempo Transcurrido: {elapsed_time}."
                    )
                )
                order.state = next_state

            elif current_state == 'cost_approval':
                if not order.cost_approval:
                    raise UserError("Se requiere la aprobación de costos para confirmar el pedido.")
                order.costs_to_confirmed_date = fields.Datetime.now()
                local_time = self._convert_to_user_timezone(order.costs_to_confirmed_date)
                tz_name = self.env.user.tz or 'UTC'
                elapsed_time = self._compute_elapsed_time(order.manager_to_costs_date, order.costs_to_confirmed_date)
                order.message_post(
                    body=(
                        f"El estado pasó de 'Aprobación de Costos' a 'Pedido Confirmado' el {local_time.strftime('%Y-%m-%d %H:%M:%S')} ({tz_name}) "
                        f"por el usuario: {self.env.user.name}.<br>"
                        f"Tiempo Transcurrido: {elapsed_time}."
                    )
                )
                order.state = next_state
                # Call parent method to handle project creation and other standard behaviors
                return super(SaleOrder, self).action_confirm()

        return True

    def approve_manager(self):
        """
        El gerente aprueba el pedido solo si el flujo está habilitado.
        """
        self.ensure_one()
        if not self.company_id.use_approval_flow:
            raise UserError("El flujo de aprobaciones no está habilitado para esta compañía.")

        if not self.env.user.has_group('permisos_equipos_ventas.group_sale_team_manager'):
            raise AccessError("No tienes los permisos necesarios para aprobar como gerente.")
        
        self.write({'manager_approval': True})
        self.action_confirm()

    def approve_costs(self):
        """
        Contabilidad aprueba los costos solo si el flujo está habilitado.
        """
        if not self.company_id.use_approval_flow:
            raise UserError("El flujo de aprobaciones no está habilitado para esta compañía.")

        if not self.env.user.has_group('account.group_account_manager'):
            raise AccessError("No tienes los permisos necesarios para aprobar costos.")
        
        self.cost_approval = True
        self.action_confirm()

    def reject_approval(self):
        self.ensure_one()
        if not self.rejection_reason:
            raise UserError("Please provide a rejection reason")
