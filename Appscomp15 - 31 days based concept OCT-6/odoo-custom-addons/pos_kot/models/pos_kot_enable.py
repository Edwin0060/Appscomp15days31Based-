from odoo import models, fields ,api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    kot = fields.Boolean(string='Enable Kitchen Order Print')