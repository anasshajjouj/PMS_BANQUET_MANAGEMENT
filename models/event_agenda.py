from odoo import models, fields

class EventAgenda(models.Model):
    _name = 'event.agenda'
    _description = 'Event Agenda'

    date = fields.Date(string='Date', required=True)
    time_start = fields.Float(string='Start Time', required=True)
    time_end = fields.Float(string='End Time', required=True)
    number_visitor = fields.Integer(string='Number of Visitors')
    event_type_id = fields.Many2one('event.type', string='Event Type', required=True, ondelete='cascade')

class EventType(models.Model):
    _inherit = 'event.type'

    agenda_ids = fields.One2many('event.agenda', 'event_type_id', string='Agenda Planning')
