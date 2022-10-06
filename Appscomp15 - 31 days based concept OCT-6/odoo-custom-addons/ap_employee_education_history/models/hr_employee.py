from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_wrk_hist_ids = fields.One2many('employee.education.history', 'employee_id')
    salary_revision_ids = fields.One2many('employee.salary.revision', 'employee_id')
    # attachment = fields.Binary(String="Attachments")
    attachment = fields.Many2many('ir.attachment', String="Attachments")
    attachment_name = fields.Char(string="Education Attachment")


class EmployeeDepartment(models.Model):
    _name = 'employee.department'
    _description = 'Department'

    name = fields.Char(string="Department")


class EmployeeLevel(models.Model):
    _name = 'employee.level'
    _description = 'Employee Level'

    name = fields.Char(string="Level")


class EmployeeDegree(models.Model):
    _name = 'employee.degree'
    _description = 'Employee Degree'

    name = fields.Char(string="Degree")


class EmployeeInstitute(models.Model):
    _name = 'employee.institute'
    _description = 'Employee Institute'

    name = fields.Char(string="Institute")


class EmployeeEducationHistory(models.Model):
    _name = 'employee.education.history'
    _description = 'Employee Education History'

    employee_id = fields.Many2one('hr.employee')
    department_id = fields.Many2one('employee.department', string="Department")
    degree_id = fields.Many2one('employee.degree', string="Degree")
    # level_id = fields.Many2one('employee.level', string="Level")
    level_id = fields.Char(string="Level")
    institute_id = fields.Many2one('employee.level', string="Institute")
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    # attachment = fields.Many2many('ir.attachment', String="Attachments")
    attachment = fields.Binary(String="Attachments")
    detail = fields.Char(string="Specialization")
    attachment_name = fields.Char(string="Education Details")


class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    expertise_in = fields.Char(string="Expertise In")
    relieved_reason = fields.Char(string="Relieved Reason")
    salary = fields.Float(string="Salary")
    experience = fields.Char(string="Experience")


class EmployeeSalaryRevision(models.Model):
    _name = 'employee.salary.revision'

    employee_id = fields.Many2one('hr.employee')
    new_salary_from = fields.Date(string="New Salary From")
    new_salary_amount = fields.Float(string="New Salary Amount")
    old_salary_amount = fields.Float(string="Old Salary Amount")
    salary_hike = fields.Float(string="Salary Hike(%)")
    new_salary_id = fields.Many2one('res.users', default=lambda self: self.env.uid, string="Approved By")
    job_position_id = fields.Many2one('hr.job')
    department_id = fields.Many2one('hr.department')
    level = fields.Char()

    @api.onchange('new_salary_amount', 'old_salary_amount')
    def onchange_hike_percentage(self):
        # print("helloooooo")
        if self.new_salary_amount > 0 and self.old_salary_amount > 0:
            # print("salry is greater than zero++++++++++++++++++++++++++++++++++",
            #       self.new_salary_amount > 0 and self.old_salary_amount > 0)
            difference = self.new_salary_amount - self.old_salary_amount
            # print("the difference between the salriessssssssss====================================================",
            #       difference)
            # print("the percentage of the salary====================================================",
            #       difference)
            if difference > 0:
                # print("the Difference value is greater than zero")
                percentage = difference / self.old_salary_amount
                # print("the percentage is to be calculated",percentage)
                actual_percenatage = percentage * 100
                # print("The Actual percentage is calculted",actual_percenatage)
                percentage_float = "{:.2f}".format(actual_percenatage)
                # print("The float percentage is only shown 2 digits",percentage_float)
                self.write({
                    'salary_hike': actual_percenatage
                })
