from odoo import fields, models, api, _


class Leave(models.Model):
    _name = 'leave.description.master'
    _description = 'Leave Description Master'

    name = fields.Char(string="Leave")
    date = fields.Date(string="Date")
    days = fields.Float(string="Days", compute='get_leave_details')

    # def get_leave_details(self):
    #     employee_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
    #     employee_leave_aa = self.env['hr.leave'].search(
    #         [('employee_id', '=', self.employee_id.id), ('holiday_status_id.name', '=', 'Annual Leaves')])
    #     num_days = 0
    #     for aa in employee_leave_aa:
    #         employee_leave = self.env['hr.leave'].search_count(
    #             [('employee_id', '=', self.employee_id.id), ('holiday_status_id.name', '=', 'Annual Leaves'),
    #              ('state', '=', 'validate')])
    #
    #         import calendar
    #         import datetime
    #         date = datetime.datetime.now()
    #         diff = calendar.monthrange(date.year, date.month)[1]
    #
    #         num_days += aa.number_of_days
    #         print('Employee Annual Leaves count', num_days)
    #         print('hiiiiiiiii', employee_contract)
    #         print('hiiiiiiiii', employee_leave)

    class PublicholidayLeave(models.Model):
        _inherit = "hr.public.holidays"
        _description = 'Public Holiday'

        # name_id = fields.Char(string='Name')
        year_id = fields.Many2one('hr.payroll.year', string="Year", required='1')
