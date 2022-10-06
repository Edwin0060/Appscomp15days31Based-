# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning, ValidationError, UserError
from datetime import date, timedelta
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_om_hr_payroll_account = fields.Boolean(string='Payroll Accounting')


class HrPayrollMonth(models.Model):
    _name = 'hr.payroll.month'
    _description = 'Payroll Month Master Config'

    name = fields.Char(string='Month')


class HrPayrollyear(models.Model):
    _name = 'hr.payroll.year'
    _description = 'Payroll Year Master Config'

    name = fields.Char(string='Year')
    day_and_month = fields.One2many('hr.payroll.year.line', 'name_id')
    month = fields.Char(string='month', compute='_compute_month')


    @api.depends('month')
    @api.onchange('month')
    def _compute_month(self):
        import datetime
        date = datetime.datetime.now()
        daten = datetime.datetime(1, int(date.month), 1).strftime("%B")
        self.month = daten

    # @api.constrains('name')
    # def _check_name(self):
    #     for record in self:
    #         if record.name:
    #             domain = [('name', '=', record.name)]
    #             name = self.search(domain)
    #             if len(name) > 1:
    #                 for i in range(len(name)):
    #                     if name[i].id != record.id:
    #                         raise ValidationError(
    #                             _('Alert !!  Year - %s already exists.') % (
    #                                 record.name))

    @api.onchange('day_and_month')
    def _public_holiday(self):
        for record in self.day_and_month:
            public_leave_count = 0.00
            employee_public_leave = record.env['hr.public.holidays.line'].sudo().search(
                [('month', '=', record.select_month)])
            for line in employee_public_leave:
                if record.select_month == line.month:
                    public_leave_count += 1
                # num.append(line.name)
            record.public_holiday_count = public_leave_count
            num = ''
            for rec in employee_public_leave:
                if record.select_month == rec.month:
                    num += str(rec.name) + ','
                record.holiday_public = num


    def find_all_sundays(self):
        import datetime
        import calendar
        today = datetime.date.today()
        day = datetime.date(today.year, today.month, 1)
        single_day = datetime.timedelta(days=1)
        sundays = 0
        date = datetime.datetime.now()
        diff = calendar.monthrange(date.year, date.month)[1]
        date = datetime.datetime.now()
        daten = datetime.datetime(1, int(date.month), 1).strftime("%B")
        # self.month = daten
        while day.month == today.month:
            if day.weekday() == 6:
                sundays += 1
            day += single_day
        for line in self.day_and_month:
            if line.select_month == self.month:
                line.sunday = sundays + 1
                line.number_of_days = diff - (line.sunday + line.public_holiday_count)


    def get_number_of_working_days(self):
        num_of_days = self.env['hr.payslip'].search([('date_year', '=', self.name)])
        for line in num_of_days:
            if line.date_months == self.month:
                line.write({
                    'number_working_of_days': self.day_and_month.number_of_days})


#
#
#     for slip in self:
#         # print('222222222222222222222222222222222222222222222222222222222222222')
#         if num_of_days.date_months == slip.day_and_month.month:
#             # print('33333333333333333333333333333333333333333333333333333333' , num_of_days.date_months ,slip.day_and_month.month , num_of_days.date_months == slip.day_and_month.month )
#             for line in num_of_days:
#                 # print('44444444444444444444444444444444444444444444444444444444' ,)
#                 if line.number_of_working_days == 0.0:
#                     # print('555555555555555555555555555555555555555555555555555555555555555555555555555',line.number_of_working_days == 0.0 )
#                     line.number_of_working_days = slip.day_and_month.number_of_days
#                     # print('6666666666666666666666666666666666666666666666666666' ,line.number_of_working_days , slip.day_and_month.number_of_days)


class Monthyear(models.Model):
    _name = 'hr.payroll.year.line'
    _description = 'Payroll Year  line'

    name_id = fields.Many2one('hr.payroll.year', string='Year')
    # month = fields.Char(string='Month')
    number_of_days = fields.Float(string='Number Of Days')
    week_off = fields.Selection([('weekoff', 'All Sundays & 3rd Saturday')], default='weekoff', string='Week Off')
    sunday = fields.Integer(string='Sunday')
    boolen_leave = fields.Boolean(string='Approved')
    select_month = fields.Selection([
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ], string="Month")
    public_holiday_id = fields.Many2many('hr.holidays.public', string='Public Holidays')
    # holiday_date = fields.Date(string='Date')
    public_holiday_count = fields.Integer(string='Public Holiday Count')
    holiday_public = fields.Char(string='Leave Type')

    def action_approve(self):
        from datetime import datetime
        currentMonth = datetime.now().month
        if self.name_id.month == self.select_month:
            self.write({'boolen_leave': True})
            self.name_id.find_all_sundays()
            self.name_id.get_number_of_working_days()

    # @api.constrains('select_month')
    # def _check_select_month(self):
    #     for record in self:
    #         if record.select_month:
    #             domain = [('select_month', '=', record.name_id.month)]
    #             name = self.search(domain)
    #             if len(name) > 1:
    #                 for i in range(len(name)):
    #                     if name[i].id != record.id:
    #                         raise ValidationError(
    #                             _('Alert !!  Selected Month of - %s already exists.') % (
    #                                 record.select_month))

    # @api.onchange('public_holiday_id', 'holiday_date')
    # def onchange_date(self):
    #     self.holiday_date = self.public_holiday_id.line_ids.date
    #     print('**************************************************************', self.public_holiday_id.line_ids.date)

    # def action_approve(self):
    #     from datetime import datetime
    #     currentMonth = datetime.now().month
    #     if self.name_id.month == self.select_month:
    #         self.write({'boolen_leave': True})
    #         self.name_id.find_all_sundays()
    #         self.name_id.get_number_of_working_days()

    # @api.constrains('select_month')
    # def _check_select_month(self):
    #     for record in self:
    #         if record.select_month:
    #             domain = [('select_month', '=', record.name_id.month)]
    #             name = self.search(domain)
    #             if len(name) > 1:
    #                 for i in range(len(name)):
    #                     if name[i].id != record.id:
    #                         raise ValidationError(
    #                             _('Alert !!  Selected Month of - %s already exists.') % (
    #                                 record.select_month))

    # @api.onchange('public_holiday_id', 'holiday_date')
    # def onchange_date(self):
    #     self.holiday_date = self.public_holiday_id.line_ids.date
    #     print('**************************************************************', self.public_holiday_id.line_ids.date)
