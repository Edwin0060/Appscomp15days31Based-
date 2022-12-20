from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = "pos.order"

    order_date = fields.Date(compute="compute_order_date", store=True, string='Order Date')

    @api.depends('date_order')
    def compute_order_date(self):
        for line in self:
            if line.date_order:
                line.order_date = line.date_order.date()
