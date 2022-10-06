# -*- coding:utf-8 -*-

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date, datetime
from datetime import date, timedelta
from odoo.exceptions import ValidationError, Warning


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True)
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count',
                                   groups="om_om_hr_payroll.group_hr_payroll_user")
    date_of_joining = fields.Date(string='Date Of Joining', required=True)
    actual_carry_over_remarks = fields.Char(string='Approver Remarks')
    carry_over = fields.Boolean(String='Carry Over')
    carry_over_approved_by = fields.Char(string="Carry Over Approved By")
    carry_over_approved_date = fields.Datetime(string="Carry Over Approved By")
    actual_carry_over_leave = fields.Float(string='Balance Carry Over Leave')
    approved_leave = fields.Float(string='Carry Over Approved Leave')
    internal_leave_deduction = fields.Float(string='Internal Leave Deduction')
    # eligible_period = fields.Selection[('1_month', '1 Month'),('2_month', '2 Month'),('3_month', '3 Month'),
    # ('4_month', '4 Month'),('5_month', '5 Month'),('6_month', '6 Month'),]
    # eligible_period = fields.Selection([('1_month', '1 Month'), ('2_month', '2 Month'), ('3_month', '3 Month'),
    #                                     ('4_month', '4 Month'), ('5_month', '5 Month'), ('6_month', '6 Month'),
    #                                     ('7_month', '7 Month'), ('8_month', '8 Month')
    #                                        , ('9_month', '9 Month'), ('10_month', '10 Month')
    #                                        , ('11_month', '11 Month'), ('12_month', '12 Month')],
    #                                    string='Eligible Period', default='12_month')
    # ~ universal_account_number = fields.Char(string='UAN', help='Universal account number')
    # ~ permanent_account_number = fields.Char(string='PAN', help='Permanent account number')
    # ~ pf_number = fields.Char(string="PF Number")
    # ~ work_type = fields.Selection([('call_centre','Call Centre'),('it','IT'),('others','Others')],string='Work Type')
    # ~ training_end_date = fields.Date(string='Training End Date')
    # last_day_of_current_month = date.today() + relativedelta(day=31)
    last_day_of_current_month = date.today() + timedelta(days=30)
    emergency_contact_one = fields.Char(string="Emergency Contact")
    emergency_contact_two = fields.Char(string="Alternative Emergency Contact")
    emergency_phone_one = fields.Integer(string="Emergency Phone")
    emergency_phone_two = fields.Integer(string="Alternative Emergency Phone")
    optional_holiday = fields.Boolean(string="Optional holiday approved?")
    optional_holiday_limit = fields.Integer(string="Optional Holiday Limit")
    optional_holiday_utilised = fields.Integer(string="Optional Holiday Utilised")
    employee_eligible_period = fields.Integer(string='Eligible Period After', store=True, default=1)
    leave_eligible_date = fields.Date(string='CL Eligible Date')
    rl_leave_eligible_date = fields.Date(string='RL Eligible Date')
    cl_three_days_consumed = fields.Boolean(string="CL 3 Days Consumed ?")
    rl_three_days_consumed = fields.Boolean(string="RL 3 Days Consumed ?")
    age = fields.Char(string='Age', compute='_compute_age')
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    employee_first_contract_date = fields.Date(string="First Contract Date",compute='employee_contract_date')

    @api.depends('date_of_joining', 'employee_first_contract_date')
    @api.onchange('date_of_joining','employee_first_contract_date')
    def employee_contract_date(self):
        if self.name and self.date_of_joining:
            self.write({'employee_first_contract_date':self.contract_id.start_date_doj,'joining_date':self.contract_id.start_date_doj})


    def _compute_payslip_count(self):
        for employee in self:
            employee.payslip_count = len(employee.slip_ids)

    @api.depends('birthday')
    def _compute_age(self):
        self.age = 0
        if self.birthday:
            years = relativedelta(date.today(), self.birthday).years
            months = relativedelta(date.today(), self.birthday).months
            day = relativedelta(date.today(), self.birthday).days
            self.age = str(int(years)) + ' Year/s ' + str(int(months)) + ' Month/s ' + str(day) + ' Day/s'

    @api.onchange('employee_eligible_period', 'date_of_joining' 'leave_eligible_date')
    def find_leave_eligible_date(self):
        for rec in self:
            if rec.date_of_joining or rec.employee_eligible_period > 0:
                last_day_of_current_month = rec.date_of_joining
                if last_day_of_current_month and rec.employee_eligible_period:
                    # importing pandas as pd
                    import pandas as pd
                    # Creating the Series
                    sr = pd.Series(pd.date_range(last_day_of_current_month,
                                                 periods=rec.employee_eligible_period, freq='M'))
                    domain = []
                    for line in sr:
                        domain.append(line)
                    current_day = last_day_of_current_month.day
                    rec.leave_eligible_date = line + timedelta(days=current_day)
            if rec.leave_eligible_date or rec.employee_eligible_period > 0:
                last_day_of_current_month = rec.leave_eligible_date
                if last_day_of_current_month and rec.employee_eligible_period:
                    # importing pandas as pd
                    import pandas as pd
                    # Creating the Series
                    sr = pd.Series(pd.date_range(last_day_of_current_month,
                                                 periods=rec.employee_eligible_period, freq='M'))
                    domain = []
                    for line in sr:
                        domain.append(line)
                    current_day = last_day_of_current_month.day
                    rec.rl_leave_eligible_date = line + timedelta(days=current_day)
            else:
                raise Warning('Alert, Eligible Period define value should be Greater than Zero!')



