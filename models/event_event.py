from odoo import models, fields, api

class EventEvent(models.Model):
    _inherit = 'event.event'

    name = fields.Char(string='Event Name', required=True, help='Name of the event.')
    organizer_id = fields.Many2one('res.partner', string='Organizer', required=True, help='Organizer of the event.')
    banquet_type = fields.Many2one('banquet.type', string="Event Type", help='Type of banquet for the event.')
    event_activity_ids = fields.One2many('event.activity', 'event_id', string="Activities", help='Activities related to the event.')
    address_id = fields.Many2one('res.partner', string='Venue', help='Venue where the event is held.')
    group_ids = fields.Many2one('event.group', string='Group Associated', help='Group associated with the event.')

    feedback_url = fields.Char(string='Feedback URL', compute='_compute_feedback_url', store=True)
    # @api.depends('id')
    def _compute_feedback_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.feedback_url = f'{base_url}/feedback?event_id={record.id}'

    def open_form_view(self):
        """
        Opens the sale order form view with pre-filled context based on the event details.

        :return: Dictionary specifying the action to open the sale order form view.
        """
        organizer_partner_id = self.organizer_id.id
        event_id = self.id
        banquet_type_id = self.banquet_type.id
        return {
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,
            'context': {
                'default_partner_id': organizer_partner_id,
                'default_event_id': event_id,
                'default_banquet_type_id': banquet_type_id,
            }
        }

    def open_calendar_planning(self):
        """
        Opens the calendar event form view with pre-filled context based on the event details.

        :return: Dictionary specifying the action to open the calendar event form view.
        """
        organizer_partner_id = self.organizer_id.id
        banquet_type_id = self.banquet_type.id
        event_id = self.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'view_id': self.env.ref('calendar.view_calendar_event_form').id,
            'target': 'new',
            'context': {
                'default_organizer_id': organizer_partner_id,
                'default_event_id': event_id,
                'default_banquet_type_id': banquet_type_id,
            }
        }

class EventAgendaWizard(models.TransientModel):
    _name = 'event.agenda.wizard'
    _description = 'Event Agenda Planning Wizard'

    date_start = fields.Datetime(string='Start Date', required=True, help='Start date of the event.')
    date_end = fields.Datetime(string='End Date', required=True, help='End date of the event.')
    time_start = fields.Float(string='Start Time', required=True, digits=(2, 2), help='Start time of the event in hours.')
    time_end = fields.Float(string='End Time', required=True, digits=(2, 2), help='End time of the event in hours.')
    number_of_visitor = fields.Integer(string='Number of Visitors', required=True, help='Estimated number of visitors.')
    event_type_id = fields.Many2one('banquet.type', string='Event Type', required=True, help='Type of banquet for the event.')
    organizer_id = fields.Many2one('res.partner', string='Organizer', required=True, help='Organizer of the event.')
    number_of_days = fields.Integer(string='Number of Days', compute='_compute_number_of_days', store=True, help='Number of days of the event.')
    agenda_line_ids = fields.One2many('event.agenda.line', 'wizard_id', string='Agenda Lines', help='Lines detailing the event agenda.')

    @api.depends('date_start', 'date_end')
    def _compute_number_of_days(self):
        """
        Computes the number of days between the start and end dates of the event.

        :return: None
        """
        for record in self:
            if record.date_start and record.date_end:
                record.number_of_days = (record.date_end.date() - record.date_start.date()).days + 1
                # Create agenda lines for each day
                record._create_agenda_lines()
            else:
                record.number_of_days = 0

    def _create_agenda_lines(self):
        """
        Creates agenda lines for each day of the event that does not already have a line.

        :return: None
        """
        self.ensure_one()
        existing_days = set(line.day for line in self.agenda_line_ids)
        new_days = set(range(1, self.number_of_days + 1))
        days_to_create = new_days - existing_days

        for day in days_to_create:
            self.env['event.agenda.line'].create({
                'wizard_id': self.id,
                'day': day,
            })

    @api.model
    def default_get(self, fields):
        """
        Overrides the default_get method to set default values based on the context.

        :param fields: List of fields to fetch default values for.
        :return: Dictionary of default values for the wizard.
        """
        res = super(EventAgendaWizard, self).default_get(fields)
        default_organizer_id = self._context.get('default_organizer_id')
        if default_organizer_id:
            res['organizer_id'] = default_organizer_id
        return res

    def create_agenda(self):
        """
        Creates agenda entries based on the wizard data and selected agenda lines.

        :return: Dictionary specifying the action to close the wizard.
        """
        event_id = self._context.get('default_event_id')
        if event_id:
            event = self.env['event.event'].browse(event_id)
            for line in self.agenda_line_ids:
                agenda_vals = {
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    'time_start': self.time_start,
                    'time_end': self.time_end,
                    'number_visitor': self.number_of_visitor,
                    'event_type_id': self.event_type_id.id,
                    'event_id': event.id,
                    'program_details': line.Activities,
                    'day': line.day,
                }
                self.env['event.agenda'].create(agenda_vals)
        return {'type': 'ir.actions.act_window_close'}

class EventAgendaLine(models.TransientModel):
    _name = 'event.agenda.line'
    _description = 'Event Agenda Line'

    wizard_id = fields.Many2one('event.agenda.wizard', string='Wizard', required=True, help='Reference to the agenda wizard.')
    day = fields.Integer(string='Day', required=True, help='Day number in the agenda.')
    Activities = fields.Text(string='Program Details', help='Details of the agenda for this day.')
    time = fields.Float(string="Time", help='Time associated with the agenda line in hours.')
    Product_list = fields.Many2one("pack.products", string="Product List", help='List of products related to the agenda line.')
