from odoo import api, fields, models


class Configuration(models.Model):
    _inherit = 'pos.config'

    image = fields.Binary(string='Image')


