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
    amount_deduction = fields.Float(string='Total Deduction', compute='compute_total_deduction')
    contract_amount_sub = fields.Float(string='Allowance Deducted Amount')

    @api.onchange('line_ids', 'contract_amount_sub')
    def contract_amount_subtraction(self):
        contract_valdiate = self.env['hr.contract'].sudo(). \
            search([('employee_id', '=', self.employee_id.id)])
        if self.employee_id:
            allowance_amount_diff = contract_valdiate.house_rent_allowance + contract_valdiate.convenyance_allowance + contract_valdiate.special_allowance + contract_valdiate.travel_incentives + contract_valdiate.health_insurance
            total_dedu_amount = 0
            sum = 0
            for value in self.line_ids:
                if value.category_id.code == 'ALW':
                    sum = sum + round(value.amount)
            total_dedu_amount = round(allowance_amount_diff) - sum
            self.contract_amount_sub = abs(total_dedu_amount)

    @api.depends('line_ids')
    @api.onchange('line_ids')
    def compute_total_deduction(self):
        for slip in self:
            total_deduction_new = 0.0
            for line in slip.line_ids:
                if line.category_id.name == 'Deduction' and line.name != 'Unpaid':
                    total_deduction_new += line.total
            slip.amount_deduction = total_deduction_new

    @api.depends('line_ids')
    @api.onchange('line_ids')
    def compute_total_amount(self):
        for slip in self:
            total_amount_new = 0.0
            for line in slip.line_ids:
                if line.salary_rule_id.code == 'NET':
                    total_amount_new += line.total
            slip.total_amount = round(total_amount_new)

    def _compute_num2words(self):
        self.amount_words = (num2words.num2words(self.total_amount, lang='en')).capitalize()
