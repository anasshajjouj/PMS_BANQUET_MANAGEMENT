from odoo import api, fields, models
from odoo.fields import Command
from odoo import http
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    banquet_type_id = fields.Many2one('banquet.type', string='Banquet Type',
                                      help='Select the banquet type for the sale order.')
    job_category_id = fields.Many2one('job.category', string='Category',
                                      domain="[('banquet_id', '=', banquet_type_id)]",
                                      help='Select the job category related to the banquet type.')

    available_partner_ids = fields.Many2many('res.partner', compute='_compute_available_partners')

    available_job_category_ids = fields.Many2many('job.category', compute='_compute_available_job_categories',
                                                  string='Available Job Categories')
    event_date_b = fields.Datetime(string='Event Start Date')
    event_date_e = fields.Datetime(string='Event Start Date')

    event_id = fields.Many2one('event.event', string='Event', domain="[('organizer_id', '=', partner_id)]")
    event_name = fields.Char(related='event_id.name', string='Event Name', store=True)
    event_date_end = fields.Datetime(related='event_id.date_end', string='Event End Date', store=True)
    event_type_name = fields.Many2one(related='event_id.banquet_type', string='Event type', store=True)
    event_date_begin = fields.Datetime(related='event_id.date_begin', string='Event Start Date', store=True)
    event_organizer_id = fields.Many2one(related='event_id.organizer_id', string="custom-addons")

    def open_agenda_planning(self):
        organizer_partner_id = self.event_organizer_id.id
        banquet_type_id = self.event_type_name.id
        banquet_name = self.banquet_type_id.id
        job_category_ids = self.order_line.mapped('job_category_id').ids
        event_id = self.event_id.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'planning.slot',
            'view_mode': 'form',
            'view_id': self.env.ref('planning.planning_view_form').id,
            'target': 'new',
            'context': {
                'default_organizer_id': organizer_partner_id,
                'default_banquet_type_id': banquet_type_id,
                'default_job_category_ids': [(6, 0, job_category_ids)],
                'default_event_id': event_id,
                'default_banquet_name': banquet_name,
            }
        }

    @api.onchange('company_id')
    def _onchange_company_id(self):
        for line in self.order_line:
            line.company_id = self.company_id.id
            line._onchange_company_id()

    def action_confirm(self):
        """Override the action_confirm method to create stock moves
        for pack products."""
        super().action_confirm()
        for line in self.order_line:
            if line.product_id.is_pack:
                for record in line.product_id.pack_products_ids:
                    for rec in self.picking_ids:
                        move = rec.move_ids.create({
                            'name': record.product_id.name,
                            'product_id': record.product_id.id,
                            'product_uom_qty': record.quantity * line.product_uom_qty,
                            'product_uom': record.product_id.uom_id.id,
                            'picking_id': rec.id,
                            'location_id': rec.location_id.id,
                            'location_dest_id': rec.location_dest_id.id,
                        })
                        move._action_confirm()


@api.depends('banquet_type_id')
def _compute_available_job_categories(self):
    for order in self:
        if order.banquet_type_id:
            order.available_job_category_ids = order.banquet_type_id.job_category_ids
        else:
            order.available_job_category_ids = self.env['job.category'].search([])


@api.depends('job_category_ids')
def _compute_available_partners(self):
    for order in self:
        partners = self.env['res.partner']
        for category in order.job_category_ids:
            partners |= category.personnel_ids
        order.available_partner_ids = partners
        order.selected_partner_ids = False


@api.onchange('job_category_ids')
def onchange_job_category_ids(self):
    self._add_category_sections()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    banquet_type_id = fields.Many2one('banquet.type', string='Banquet Type',
                                      help='Select the banquet type for the sale order.')
    job_category_id = fields.Many2one('job.category', string='Category',
                                      domain="[('banquet_id', '=', banquet_type_id)]",
                                      help='Select the job category related to the banquet type.')
    product_template_id = fields.Many2one('product.template', compute='_compute_product_template', store=True,
                                          string='Product Template')
    personnel_ids = fields.Many2many(related="job_category_id.personnel_ids")
    partner_id = fields.Many2one("res.partner", string="Select partner")
    pack_ids = fields.One2many(related="partner_id.product_pack_ids")

    @api.depends('product_id')
    def _compute_product_template(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id if line.product_id else False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_template_id = self.product_id.product_tmpl_id
            self.price_unit = self.product_id.list_price

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = {
            'display_type': self.display_type or 'product',
            'sequence': self.sequence,
            'name': self.name,
            # 'job_category_id': self.job_category_id.id,
            # 'banquet_type_id': self.banquet_type_id.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [Command.set(self.tax_id.ids)],
            'sale_line_ids': [Command.link(self.id)],
            'is_downpayment': self.is_downpayment,
        }
        analytic_account_id = self.order_id.analytic_account_id.id
        if self.analytic_distribution and not self.display_type:
            res['analytic_distribution'] = self.analytic_distribution
        if analytic_account_id and not self.display_type:
            analytic_account_id = str(analytic_account_id)
            if 'analytic_distribution' in res:
                res['analytic_distribution'][analytic_account_id] = res['analytic_distribution'].get(
                    analytic_account_id, 0) + 100
            else:
                res['analytic_distribution'] = {analytic_account_id: 100}
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    event_name = fields.Char(string='Event Name')
    event_organizer = fields.Many2one('res.partner', string='Event Organizer')
    folder_id = fields.Many2one('invoice.folder', string='Invoice Folder')

class WebsiteSaleOrder(http.Controller):

    @http.route('/quote/configure', type='http', auth='public', website=True)
    def quote_configure(self, **kw):
        partners = request.env['res.partner'].search([])
        job_categories = request.env['job.category'].search([])
        products = request.env['product.template'].search([])
        return request.render('event_management_odoo.quote_configure_template', {
            'partners': partners,
            'job_categories': job_categories,
            'products': products,
        })

    @http.route('/get/product_price', type='json', auth='public')
    def get_product_price(self, product_id):
        product = request.env['product.product'].browse(int(product_id))
        return {'price': product.lst_price}

