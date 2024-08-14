from odoo import api, fields, models

class BanquetDetails(models.Model):
    _name = 'banquet.details'
    _description = 'Banquet Details'

    name = fields.Char(string='Detail Name', required=True)
    banquet_id = fields.Many2one('banquet.type', string='Banquet Type', ondelete='cascade', required=True)
    image = fields.Binary(string='Image')
    activity = fields.Char(string='Activity', required=True)
    time = fields.Float(string='Time', required=True)
    # product_ids = fields.Many2many('product.product', string='Products')
