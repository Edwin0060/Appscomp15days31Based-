from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError, UserError
from datetime import timedelta, date, datetime
from pytz import timezone, UTC
import pytz
from odoo import tools
from odoo.modules.module import get_module_resource
import base64
from lxml import etree
from dateutil import relativedelta
import re
import os
import json


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        doc = etree.XML(res['arch'])
        toolbar_action = res.get('toolbar', False) and res.get('toolbar').get('action', False)
        if toolbar_action:
            for action in toolbar_action:
                if self._context.get('emp_profile', True) and view_id == self.env.ref(
                        'appscomp_hr.my_profile_view_appscomp_hr_view').id or view_id == self.env.ref(
                    'appscomp_hr.my_profile_view_appscomp_hr_employee_tree').id:
                    toolbar_action.remove(action)
        if not self.env.user.has_group('appscomp_hr.group_employee_create_menu'):
            if view_type == 'form':
                for node in doc.xpath("//form"):
                    node.set("create", 'false')
            if view_type == 'tree':
                for node in doc.xpath("//tree"):
                    node.set("create", 'false')
            if view_type == 'kanban':
                for node in doc.xpath("//kanban"):
                    node.set("create", 'false')
        if not self.env.user.has_group('appscomp_hr.group_employee_edit_menu'):
            if view_type == 'form':
                if not self._context.get('show_emp_edit_button', False):
                    for node in doc.xpath("//form"):
                        node.set("edit", 'false')
        if view_type == 'form':
            for node in doc.xpath("//form"):
                node.set("delete", 'false')
        if view_type == 'tree':
            for node in doc.xpath("//tree"):
                node.set("delete", 'false')
        if view_type == 'kanban':
            for node in doc.xpath("//kanban"):
                node.set("delete", 'false')
        res['arch'] = etree.tostring(doc)
        return res

    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True)
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count')
    emp_code = fields.Char(string='Employee ID')
    pan_card_no = fields.Char(string='PAN Number')
    aadhar_no = fields.Char(string='Aadhar Number')
    esi_no = fields.Char(string='ESI Number')
    provident_fund_no = fields.Char(string='Provident Fund Number')
    uan_no = fields.Char(string='UAN Number')
    medical_insurance_no = fields.Char(string='Medical Insurance Number')
    work_type = fields.Selection([('call_centre', 'Call Centre'), ('it', 'IT'), ('others', 'Others')],
                                 string='Work Type')
    training_end_date = fields.Date(string='Training End Date')
    contract_employee = fields.Boolean('Contract Employee')
    check_in = fields.Datetime(string="Check In")
    # check_in_time = fields.Char(string="Check In Time")
    check_out = fields.Datetime(string="Check Out")
    # check_out_time = fields.Char(string="Check Out Time")
    duration = fields.Char(string='Time')
    mother_tongue = fields.Many2many('languages.known', string="Mother Tongue")
    blood_group = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('o+', 'O+'),
        ('o', 'O-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('a1+', 'A1+'),
        ('a1-', 'A1-'),
        ('b1+', 'B1+'),
        ('b1-', 'B1-'),
        ('b2', 'B2'),
        ('bombay', 'HH(Bombay Blood)'),
        ('others', 'Others')
    ])
    religion = fields.Selection([
        ('hindu', 'Hindu'),
        ('muslim', 'Muslim'),
        ('christian', 'Christian'),
        ('others', 'Others')
    ])
    caste = fields.Char(string="Caste")
    community = fields.Char(string="Community")
    spouse_contact = fields.Char(string="Spouse Contact")
    check_in_time = fields.Float(string='Check In Time')
    check_out_time = fields.Float(string='Check Out Time')

    def _compute_payslip_count(self):
        for employee in self:
            employee.payslip_count = len(employee.slip_ids)

    # @api.onchange('check_in', 'check_out')
    # def _check_in_check_out(self):
    #     if self.check_in:
    #         time_in = self.check_in.time()
    #         self.check_in_time = time_in
    #     if self.check_out:
    #         time_out = self.check_out.time()
    #         self.check_out_time = time_out
    #         duration = self.check_out - self.check_in
    #         self.duration = duration
    #         print('Duration  time findddddddddddddddddddd',duration)
    #
    #


class LanguagesKnown(models.Model):
    """""to select/create languages"""
    _name = 'languages.known'
    _description = 'Languages Known'

    name = fields.Char(string="Mother Tongue")


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def attendance_check_notify(self):
        emp_obj = self.env['hr.employee'].search([('work_type', '=', 'call_centre')])
        attendance_obj = self.env['hr.attendance']
        # ~ attendance_obj=self.env['hr.attendance'].search([('employee_id.work_type','=','call_centre'),('check_in','=' ,False)])
        # ~ emp_lst = [obj.employee_id for obj in attendance_obj]
        user_tz = self.env.user.tz
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(user_tz)
        current_time = old_tz.localize(datetime.now()).astimezone(new_tz).replace(tzinfo=None)
        for emp in emp_obj:
            if attendance_obj.search([('employee_id', '=', emp.id), ('check_in', '=', current_time.date())]):
                continue
            if emp.id == 1:
                continue
            query = """ select * from hr_attendance where employee_id = %s  and check_in::date  = '%s'  """ % (
                emp.id, current_time.date())
            self.env.cr.execute(query)
            attendance = self.env.cr.fetchone()
            if attendance is None:
                checkintime = str(emp.check_in).split(':')
                minute = 0
                hour = 0
                if len(checkintime) > 1:
                    minute = int(checkintime[1])
                if checkintime:
                    hour = int(checkintime[0])
                c = datetime.strptime(str(current_time.date()) + ' ' + '00:00:00', '%Y-%m-%d %H:%M:%S')
                checkindate = c + timedelta(hours=hour, minutes=minute)
                diff = checkindate - current_time
                mins = diff.seconds // 60
                print(current_time, c, mins, diff, checkindate, 'TIMEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
                # emp_time = current_time + timedelta(hours=checkintime)
                if mins == 10:
                    mail_content = "  Hello  " + emp.name + ",<br>Your attendance time  is going to start  Please Sign in before late Log "
                    main_content = {
                        'subject': _('Attendace Reminder For Sign in'),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': emp.work_email,
                    }
                    self.env['mail.mail'].sudo().create(main_content).send()


class User(models.Model):
    _inherit = ['res.users']

    payslip_count = fields.Integer(compute='_compute_payslip_count')
    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True)

    def _compute_payslip_count(self):
        for employee in self:
            employee.payslip_count = len(employee.slip_ids)

# ~ class HrPayslip(models.Model):
# ~ _name = 'hr.payslip'

# ~ total_amount = fields.Float(string='Total Amount', compute='compute_total_amount', store=True)
