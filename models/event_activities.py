from odoo import models, fields


class EventActivity(models.Model):
    _name = 'event.activity'
    _description = 'Event Activity'

    time_start = fields.Float(string='Time Start', required=True)
    time_end = fields.Float(string='Time End', required=True)
    description_event = fields.Text(string='Description', required=True)
    event_type_id = fields.Many2one('event.type', string='Event Type')
    event_id = fields.Many2one('event.event', string='Event')
    salle_event = fields.Selection([
        ('salle_a', 'Salle A'),
        ('salle_b', 'Salle B'),
        ('salle_c', 'Salle C'),
    ], string='Salle Event')
