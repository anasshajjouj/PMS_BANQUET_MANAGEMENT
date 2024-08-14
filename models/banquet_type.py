from odoo import api, fields, models

class BanquetType(models.Model):
    _name = 'banquet.type'
    _description = 'Banquet Type'

    name = fields.Char(string='Banquet Type', required=True, help='Type of banquet, e.g., wedding, corporate event.')
    banquet_detail_ids = fields.One2many('banquet.details', 'banquet_id', string='Banquet Details', help='Details associated with this banquet type.')
    job_category_ids = fields.One2many("job.category", "banquet_id", string="Job Categories", help='Categories of jobs related to this banquet type.')
    partner_ids = fields.Many2many(
        'res.partner',
        'banquet_type_res_partner_rel',
        'banquet_type_id',
        'partner_id',
        string='Partners',
        help='Partners associated with this banquet type.'
    )

    partner_count = fields.Integer(string='Number of Partners', compute='_compute_partner_count', help='Number of partners linked to this banquet type.')

    @api.depends('partner_ids')
    def _compute_partner_count(self):
        """
        Computes the number of partners linked to this banquet type.

        :return: None
        """
        for record in self:
            record.partner_count = len(record.partner_ids)

    @api.model
    def create(self, vals):
        """
        Overrides the create method to also create a corresponding product public category.

        :param vals: Dictionary of field values for the new record.
        :return: The created BanquetType record.
        """
        # Create the new banquet type record
        banquet_type = super(BanquetType, self).create(vals)

        # Create the corresponding product public category
        category_vals = {
            'name': banquet_type.name,
            'parent_id': False,  # Set to False for top-level category or to the ID of the parent category if needed
        }
        # Create the category
        self.env['product.public.category'].create(category_vals)

        return banquet_type


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    banquet_type_id = fields.Many2one('banquet.type', string='Banquet Type', help='Reference to the associated banquet type.')
