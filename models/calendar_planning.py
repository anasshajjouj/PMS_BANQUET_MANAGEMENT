from odoo import fields, api, _, models


class CalendarPlanning(models.Model):
    _inherit = 'calendar.event'

    banquet_type_id = fields.Many2one('banquet.type', string='Banquet Type', readonly=True)
    event_id = fields.Many2one('event.event', string='Event', readonly=True,
                               domain="[('organizer_id', '=', partner_id)]")
    organizer_id = fields.Many2one(string='Organizer', related='event_id.organizer_id')
    seats_limited = fields.Boolean(string='Limit Registrations', store=True)
