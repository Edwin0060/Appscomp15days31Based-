# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def get_display_stock_pos(self):
        list =[]

        display_stock_pos = self.env['ir.config_parameter'].sudo().get_param(
            'ls_pos_stock.display_stock_pos')
        list.append(display_stock_pos)

        hide_out_of_stock_pos = self.env['ir.config_parameter'].sudo().get_param(
            'ls_pos_stock.hide_out_of_stock_product')
        list.append(hide_out_of_stock_pos)

        return list

        
