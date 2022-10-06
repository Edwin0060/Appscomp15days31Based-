# -*- coding: utf-8 -*-
import logging
import pytz
import time
import babel

from odoo import _, api, fields, models, tools, _
# ~ from odoo.addons.mail.models.mail_template import format_datetime
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from datetime import datetime
from datetime import time as datetime_time
# ~ from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare, float_is_zero
import num2words


class HrPayslip(models.Model):
    # ~ _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    total_amount = fields.Float(string='Total Amount', compute='compute_total_amount', store=True)
    amount_words = fields.Char(string='Amount in Words', compute='_compute_num2words')
    amount_net_total = fields.Float(string='Total Amount')

    @api.depends('line_ids')
    @api.onchange('line_ids')
    def compute_total_amount(self):
        for slip in self:
            total_amount_new = 0.0
            for line in slip.line_ids:
                if line.salary_rule_id.code == 'NET':
                    total_amount_new += line.total
            slip.total_amount = total_amount_new

    def _compute_num2words(self):
        self.amount_words = (num2words.num2words(self.total_amount, lang='en')).capitalize()
