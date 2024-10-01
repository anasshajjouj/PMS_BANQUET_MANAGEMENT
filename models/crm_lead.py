from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    event_id = fields.Many2one('event.event', string='Related Event', help='Event related to this lead.')
