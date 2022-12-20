# -*- coding: utf-8 -*-
from odoo import fields, models, api


class DeleteRecordsUpto(models.TransientModel):
    """Class for movein moveout information."""

    _name = 'delete.records.upto'

    date = fields.Date(string="Date", default=fields.Date.context_today)

    def delete_records_upto_date(self):
        """Method call for deleting records."""
        self.env['deleted.records'].search(
            [('create_date', '<', self.date)]).unlink()
