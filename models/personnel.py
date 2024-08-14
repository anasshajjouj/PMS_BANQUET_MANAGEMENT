from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    job_category_id = fields.Many2many('job.category', 'job_category_res_partner_rel', 'partner_id', 'job_category_id',
                                       string="Job Categories")
    image = fields.Binary(string="Image")
    product_pack_ids = fields.One2many('product.template', 'partner_id', string='Product Packs')
    banquet_type_ids = fields.Many2many(
        'banquet.type',
        'banquet_type_res_partner_rel',
        'partner_id',
        'banquet_type_id',
        string='Banquet Types'
    )

