from odoo import models, fields

class InvoiceFolder(models.Model):
    _name = 'invoice.folder'
    _description = 'Invoice Folder'

    name = fields.Char(string='Folder Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    invoice_ids = fields.One2many('account.move', 'folder_id', string='Invoices')
    payment_state = fields.Selection(
        related='invoice_ids.payment_state',
        string='Payment State',
        readonly=True
    )
