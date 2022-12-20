# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _description = "Journal Item"

    sale_price_unit = fields.Float('Sale Price', compute="compute_sale_price",
                                   store=True)
    diff = fields.Float('Difference', compute="compute_sale_price", store=True)
    sale_discount = fields.Float('Sale Discount', compute="compute_sale_price", store=True)
    price_total = fields.Float('Sale Price Total', compute="compute_sale_price", store=True)
    sale_id = fields.Many2one('sale.order', 'Sale Order', compute="compute_sale_price")

    @api.depends('price_unit', 'sale_discount', 'diff', 'sale_price_unit', 'discount')
    def compute_sale_price(self):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        for rec in self:
            sale_id = self.env['sale.order'] \
                    .search([('name', '=', rec.move_id.boutique_id.name)])
            print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", sale_id)
            rec.sale_id = sale_id
            if sale_id:
                for line in sale_id.order_line:
                    if line.product_id.id == rec.product_id.id:
                        rec.sale_price_unit = line.price_unit
                    if line.discount:
                        rec.sale_discount = line.discount
                        rec.price_total = line.price_subtotal
            if rec.price_unit > rec.sale_price_unit:
                rec.diff = rec.price_unit - rec.sale_price_unit
            if rec.price_unit < rec.sale_price_unit:
                rec.diff = rec.price_unit - rec.sale_price_unit
            if rec.discount != rec.sale_discount:
                rec.diff = rec.price_total - rec.price_subtotal
