from odoo import api, fields, models


class Configuration(models.Model):
	_inherit = 'pos.config'
	
	is_enable_rounding = fields.Boolean(string='Enable Rounding',default=False)
	rounding_product_id=fields.Many2one("product.product",String="Rounding Product",domain=[('type','=','service'),('available_in_pos','=',True)],required=True)
