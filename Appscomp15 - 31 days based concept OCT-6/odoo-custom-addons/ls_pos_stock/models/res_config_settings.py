# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    display_stock_pos = fields.Boolean('Display stock in POS')

    hide_out_of_stock_product = fields.Boolean('Hide out of stock products')

    @api.model
    def get_values(self):

        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param

        res.update(
            display_stock_pos = get_param('ls_pos_stock.display_stock_pos'),
            hide_out_of_stock_product = get_param('ls_pos_stock.hide_out_of_stock_product')
        )
        return res
    
    @api.model
    def set_values(self):

        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param

        set_param('ls_pos_stock.display_stock_pos', self.display_stock_pos)
        set_param('ls_pos_stock.hide_out_of_stock_product', self.hide_out_of_stock_product)

