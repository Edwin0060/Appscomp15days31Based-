# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import date, timedelta
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_om_hr_payroll_account = fields.Boolean(string='Payroll Accounting')
    portal_allow_api_keys = fields.Boolean(String="Customer API Keys")


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
    month_number = fields.Char(string='Month Number')
    date_convert = fields.Datetime(string='Date Convert')

    @api.onchange('month', 'month_number', 'name', 'day_and_month')
    def _onchange_year_and_month(self):
        import datetime
        import calendar
        for record in self.day_and_month:
            if record.select_month == '1':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '2':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '3':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '4':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '5':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '6':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '7':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '8':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '9':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '10':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '11':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays
            if record.select_month == '12':
                selection_diff = datetime.datetime(int(self.name), int(record.select_month), 1)
                record.year_monthnumber_of_days = calendar.monthrange(selection_diff.year, selection_diff.month)[1]
                sundays = len([1 for i in calendar.monthcalendar(selection_diff.year,
                                                                 selection_diff.month) if i[6] != 0])
                record.sunday = sundays

    @api.depends('month')
    @api.onchange('month')
    def _compute_month(self):
        import datetime
        import calendar
        date = datetime.datetime.now()
        daten = datetime.datetime(1, int(date.month), 1).strftime("%B")
        self.month = daten
        # self.month_number = date.month

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                name = self.search(domain)
                if len(name) > 1:
                    for i in range(len(name)):
                        if name[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  Year - %s already exists.') % (
                                    record.name))

    @api.onchange('day_and_month')
    def _public_holiday(self):
        for record in self.day_and_month:
            public_leave_count = 0.00
            employee_public_leave = record.env['hr.public.holidays.line'].sudo().search(
                [('month_number', '=', record.select_month)])
            for line in employee_public_leave:
                if record.select_month == line.month_number:
                    public_leave_count += 1
                # num.append(line.name)
            record.public_holiday_count = public_leave_count
            num = ''
            for rec in employee_public_leave:
                if record.select_month == rec.month_number:
                    if rec.name:
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
            if line.select_month:
                line.number_of_days = line.year_monthnumber_of_days - (line.sunday + line.public_holiday_count)
                line.total_number_of_days = line.year_monthnumber_of_days

    def get_number_of_working_days(self):
        num_of_days = self.env['hr.payslip'].search([('date_year', '=', self.name)])
        for line in num_of_days:
            for record in self.day_and_month:
                convert_select_month = datetime(1, int(record.select_month), 1).strftime("%B")
                if line.date_months == convert_select_month:
                    line.write({
                        'number_working_of_days': record.number_of_days,
                        'number_of_leave': record.public_holiday_count + record.sunday,
                        'total_days_of_month': record.total_number_of_days,

                    })
                #     print('Number OF Working Days ******************' , record.number_of_days)
                # if record.number_of_days ==0:
                #     raise ValidationError(
                #         _("Alert!,The selected Payslip Period - %s, Doesn't have Number Working Days Setup."
                #           "SO, Config and payroll year and check it.") % (
                #             record.date_months))


class Monthyear(models.Model):
    _name = 'hr.payroll.year.line'
    _description = 'Payroll Year  line'

    name_id = fields.Many2one('hr.payroll.year', string='Year')
    # month = fields.Char(string='Month')
    number_of_days = fields.Float(string='Number Of Days')
    week_off = fields.Selection([('weekoff', 'All Sundays & 2nd and 4th Saturday')], default='weekoff',
                                string='Week Off')
    sunday = fields.Integer(string='Sunday')
    boolen_leave = fields.Boolean(string='Approved')
    select_month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string="Month")
    public_holiday_id = fields.Many2many('hr.holidays.public', string='Public Holidays')
    # holiday_date = fields.Date(string='Date')
    public_holiday_count = fields.Integer(string='Public Holiday')
    holiday_public = fields.Char(string='Leave Type')
    total_number_of_days = fields.Float(string='Total Number Of Days')
    year_monthnumber_of_days = fields.Float(string='year month Number Of Days')

    def action_approve(self):
        from datetime import datetime
        currentMonth = datetime.now().month
        for rec in self:
            if rec.select_month:
                rec.write({'boolen_leave': True})
                rec.name_id.find_all_sundays()
                rec.name_id.get_number_of_working_days()

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

    @api.constrains('select_month')
    def _check_name(self):
        for record in self:
            if record.select_month:
                domain = [('select_month', '=', record.select_month)]
                code = self.search(domain)
                if len(code) > 1:
                    for i in range(len(code)):
                        if code[i].id != record.id:
                            convert_select_month_vali = datetime(1, int(record.select_month), 1).strftime("%B")
                            raise ValidationError(
                                _('Alert !, The Selected Month and Year of - %s-%s is already exists.') % (
                                    convert_select_month_vali, record.name_id.name))



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
