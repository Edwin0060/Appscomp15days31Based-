from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import timedelta, date, datetime
from datetime import date, timedelta


class EmployeeLeaveEligible(models.Model):
    _name = 'employee.leave.eligible'

    employee_id = fields.Many2one('hr.employee', string="Employee ")
    leave_eligible = fields.Boolean(string='Leave Eligible ')
    leave_type = fields.Many2one('hr.leave.type', string="leave Types")
    annual_leave = fields.Float(string="Annual Leave")
    bereavement_leave = fields.Float(string="Bereavement Leave")
    sick_time_off = fields.Float(string="Sick Time Off")
    compensatory_leave = fields.Float(string="Compensatory Leave")
    study_leave = fields.Float(string="Study Leave")
    casual_leave = fields.Float(string="Casual/ Personal Leave")
    maternity_leave = fields.Float(string="Maternity Leave")
    parental_leave = fields.Float(string="Parental Leave")

class HrLeave(models.Model):
    _inherit = "hr.leave"

    today = date.today()
    is_eligible = fields.Boolean(string="Is Eligible")

    def action_confirm(self):
        self.employee_leave_eligible()
        # if self.employee_id.remaining_leaves  > 0.00:
        #     raise ValidationError(('Alert!, Mr.%s - Your not Eligable To create Leave for %s,\n Please contact your Manger') %
        #                           (self.employee_id.name, self.holiday_status_id.name))
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Time off request must be in Draft state ("To Submit") in order to confirm it.'))
        self.write({'state': 'confirm'})
        holidays = self.filtered(lambda leave: leave.validation_type == 'no_validation')
        if holidays:
            # Automatic validation should be done in sudo, because user might not have the rights to do it by himself
            holidays.sudo().action_validate()
        self.activity_update()
        return True

    def employee_leave_eligible(self):
        if self.employee_id:
            if self.employee_id.leave_eligible_date <= self.today:
                self.write({
                    'is_eligible': True, 'state': 'validate'})
            else:
                raise ValidationError(('Alert!, Mr.%s - Your not Eligable for %s') %
                                      (self.employee_id.name, self.holiday_status_id.name))

    def employee_continous_leave(self):
        if self.employee_id:
            if self.holiday_status_id.code == 'CL' or 'RL':
                if self.request_date_from and self.request_date_to:
                    from datetime import datetime
                    today = datetime.today()
                    currentMonth = datetime.now().month
                    num1 = self.request_date_from.month
                    num2 = self.request_date_to.month
                    days_num = self.number_of_days
                    date1 = str(self.request_date_from)
                    datetimeFormat = '%Y-%m-%d'
                    date2 = str(self.request_date_to)
                    date11 = datetime.strptime(date1, datetimeFormat)
                    date12 = datetime.strptime(date2, datetimeFormat)
                    common_date = date11 + timedelta(days=2)
                    if currentMonth == num1 and num2:
                        if common_date == date12:
                            if self.holiday_status_id.code == 'CL' and self.employee_id.cl_three_days_consumed == False:
                                self.employee_id.write({'cl_three_days_consumed': True})
                            else:
                                raise ValidationError(('Alert!, Mr.%s - Your not Allowed to Take %s in this month.'
                                                       ' \n Please contact your HR Department.') %
                                                      (self.employee_id.name, self.holiday_status_id.name))
                            if self.holiday_status_id.code == 'RL' and self.employee_id.rl_three_days_consumed == False:
                                self.employee_id.write({'rl_three_days_consumed': True})
                            else:
                                raise ValidationError(('Alert!, Mr.%s - Your not Allowed to Take %s in this month., \n'
                                                       ' Please contact your HR Department.') %
                                                      (self.employee_id.name, self.holiday_status_id.name))

    def action_approve(self):
        # if self.employee_id.remaining_leaves <= 0.00:
        #     raise ValidationError(
        #         ('Alert!, Mr.%s - Your not Eligable To create Leave for %s,\n Please contact your Manger') %
        #         (self.employee_id.name, self.holiday_status_id.name))
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below

        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))
        self.employee_leave_eligible()


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    is_eligible = fields.Boolean(string="Is Eligible")
    today = date.today()



    def employee_leave_eligible(self):
        if self.employee_id:
            if self.employee_id.leave_eligible_date <= self.today:
                self.write({
                    'is_eligible': True})
            else:
                raise ValidationError(('Alert!, Mr.%s - Your not Eligable for %s') %
                                      (self.employee_id.name, self.holiday_status_id.name))

    def employee_dates(self):
        join_date = self.employee_id.joining_date
        join_month = join_date.month
        currentDay = datetime.now().day
        currentMonth = datetime.now().month
        # print(currentMonth,join_date,join_month)
        if join_month == currentMonth:
            for leave in self:
                leave.write({'state': 'refuse'})
        else:
            print('False')

    def action_confirm(self):
        self.employee_leave_eligible()
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Allocation request must be in Draft state ("To Submit") in order to confirm it.'))
        res = self.write({'state': 'confirm'})
        self.activity_update()
        return res

    def action_approve(self):
        self.employee_leave_eligible()
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Allocation request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env.user.employee_id

        self.filtered(lambda hol: hol.validation_type == 'both').write(
            {'state': 'validate1', 'first_approver_id': current_employee.id})
        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        self.activity_update()




class HolidaysRequest(models.Model):
    """ Leave Requests Access specifications"""

    _inherit = "hr.leave"
    _description = "Time Off"

    state = fields.Selection(selection=[
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),  # YTI This state seems to be unused. To remove
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', default='draft', store=True, tracking=True, copy=False, readonly=False)

    def get_employee_public_holiday_details(self):
        employee_master = self.env['hr.employee'].search([('name', '=', self.employee_id.name)])
        employee_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
        employee_leave_aa = self.env['hr.leave'].search(
            [('employee_id', '=', self.employee_id.id), ('holiday_status_id.name', '=', 'Optional Holiday'),
             ('state', '=', 'validate')])
        num_days = 0
        for aa in employee_leave_aa:
            employee_leave = self.env['hr.leave'].search_count(
                [('employee_id', '=', self.employee_id.id), ('holiday_status_id.name', '=', 'Optional Holiday'),
                 ('state', '=', 'validate')])
            from datetime import date, timedelta
            import calendar
            import datetime
            date = datetime.datetime.now()
            diff = calendar.monthrange(date.year, date.month)[1]
            # print('Difference between dates in months:')
            # print('Employee name', self.employee_id.id)
            # print('Employee monthly salary', employee_contract.wage)
            # print('Employee PUBLIC-HOLIDAY_leave entry', employee_leave)
            num_days += aa.number_of_days
            # print('Employee PUBLIC leave count', num_days, employee_master)
            # print('Employee PUBLIC leave state', aa.state)
            # print(aa.request_date_from, employee_master)
            # print(aa.request_date_to, employee_master.name)
        if employee_master.optional_holiday_utilised < employee_master.optional_holiday_limit:
            employee_master.write({
                'optional_holiday_utilised': num_days
            })
        # else:
        #     raise ValidationError(('Alert, Dear Employee %s, The Optional Holiday Already consumed %s /Days, '
        #                            'You"re not Eligible for the Optional Public Holiday!. ') %
        #                           (employee_master.name, employee_master.optional_holiday_utilised))

    def action_confirm(self):
        self.get_employee_public_holiday_details()
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Time off request must be in Draft state ("To Submit") in order to confirm it.'))
        self.write({'state': 'confirm'})
        holidays = self.filtered(lambda leave: leave.validation_type == 'no_validation')
        if holidays:
            # Automatic validation should be done in sudo, because user might not have the rights to do it by himself
            holidays.sudo().action_validate()
        self.activity_update()
        return True


    @api.depends('holiday_status_id')
    def _compute_state(self):
        for holiday in self:
            if self.env.context.get('unlink') and holiday.state == 'draft':
                # Otherwise the record in draft with validation_type in (hr, manager, both) will be set to confirm
                # and a simple internal user will not be able to delete his own draft record
                holiday.state = 'draft'
            else:
                holiday.state = 'confirm' if holiday.validation_type != 'no_validation' else 'draft'
