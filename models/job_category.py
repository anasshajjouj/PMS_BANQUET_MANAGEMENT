from odoo import models, fields, api

class JobCategory(models.Model):
    _name = 'job.category'
    _description = 'Job Category'

    name = fields.Char(string="Job Title", required=True)
    banquet_id = fields.Many2one("banquet.type", string="Select banquet type", required=True)
    personnel_ids = fields.Many2many('res.partner', 'job_category_res_partner_rel', 'job_category_id', 'partner_id', string="Providers")
    sale_order_ids = fields.Many2many(
        'sale.order',
        'job_category_sale_order_rel',
        'job_category_id'
    )
    # @api.depends('personnel_ids')
    # def _compute_personnel_count(self):
    #     for record in self:
    #         record.personnel_count = len(record.personnel_ids)
