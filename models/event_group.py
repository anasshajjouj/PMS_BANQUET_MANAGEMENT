from odoo import models, fields, api

class EventGroup(models.Model):
    _name = 'event.group'
    _description = 'Event Group'

    name = fields.Char(string='Group Name', required=True)
    # organizer_id = fields.Many2one('res.partner', string='Organizer')
    event_ids = fields.One2many('event.event', 'group_ids', string='Events')

    def action_create_quotation(self):
        # Open the sale order form view without creating a new quotation
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,
            'target': 'current',
        }

class EventFeedback(models.Model):
    _name = 'event.feedback'
    _description = 'Event Feedback'

    name = fields.Char(string='Attendee Name', required=True)
    rating = fields.Selection([
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars')],
        string='Rating', required=True)
    comments = fields.Text(string='Comments')
    event_id = fields.Many2one('event.event', string='Event', required=True)

    class FeedbackController(http.Controller):

        @http.route(['/feedback'], type='http', auth="public", website=True)
        def feedback_form(self, **kwargs):
            events = request.env['event.event'].sudo().search([])
            return request.render('product_combo_pack.feedback_template', {
                'events': events
            })

        @http.route(['/feedback/submit'], type='http', auth="public", website=True, csrf=False)
        def submit_feedback(self, **kwargs):
            if kwargs:
                request.env['event.feedback'].sudo().create({
                    'name': kwargs.get('name'),
                    'rating': kwargs.get('rating'),
                    'comments': kwargs.get('comments'),
                    'event_id': int(kwargs.get('event_id'))
                })
            return request.render('product_combo_pack.feedback_thank_you_template')
