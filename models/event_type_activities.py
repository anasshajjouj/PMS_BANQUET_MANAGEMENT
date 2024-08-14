from odoo import models, fields

class EventType(models.Model):
    _inherit = 'event.type'

    event_activity_ids = fields.One2many('event.activity', 'event_type_id', string='Activities')
