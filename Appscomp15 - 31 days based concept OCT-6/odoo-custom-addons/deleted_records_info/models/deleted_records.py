# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields


class DeletedRecords(models.Model):
    _name = "deleted.records"
    _description = "Stores deleted records."

    name = fields.Char(string="Name")
    model_id = fields.Many2one('ir.model', string="Model")
    user_id = fields.Many2one('res.users', string="Deleted By")
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this journal")

    def delete_past_records(self):
        save_history_days = self.env['res.config.settings'].search(
            [])[-1].save_history_days
        if save_history_days:
            date_N_days_ago = datetime.now() - timedelta(
                days=save_history_days)
            # remove microseconds from datetime object
            date_N_days_ago = date_N_days_ago.replace(microsecond=0)
            self.sudo().search(
                [('create_date', '<', str(date_N_days_ago))]).unlink()
