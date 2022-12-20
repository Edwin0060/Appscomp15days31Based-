# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    save_history_days = fields.Integer(
        string="CLear History",
        help="Delete reocrds which are older than field value.")

    @api.model
    def default_get(self, fields):
        res = super(ResConfigSettings, self).default_get(fields)
        for data in self.search([]):
            res.update({
                'save_history_days': data.save_history_days,
            })
        return res
