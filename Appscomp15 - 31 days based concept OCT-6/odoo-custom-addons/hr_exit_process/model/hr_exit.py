# -*- coding: utf-8 -*-

import time

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError


class hr_exit_checklist(models.Model):
    _name = 'hr.exit.checklist'

    name = fields.Char(string="Name", required=True)
    responsible_user_id = fields.Many2one('res.users', string='Responsible User', required=True)
    notes = fields.Text(string="Notes")
    checklist_line_ids = fields.One2many('hr.exit.checklist.line', 'checklist_line_id', string='Checklist')


class hr_exit_checklist_line(models.Model):
    _name = 'hr.exit.checklist.line'

    name = fields.Char(string="Name", required=True)
    checklist_line_id = fields.Many2one('hr.exit.checklist', invisible=True)


class hr_exit_line(models.Model):
    _name = 'hr.exit.line'
    _description = "Exit Lines"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'checklist_id'
    _order = 'id desc'

    checklist_id = fields.Many2one('hr.exit.checklist', string="Checklist", required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    notes = fields.Text(string="Remarks")
    state = fields.Selection(selection=[('draft', 'New'),
                                        ('confirm', 'Confirmed'),
                                        ('approved', 'Approved'),
                                        ('reject', 'Rejected'),
                                        ('cancel', 'Cancelled')],
                             string='State', default='draft', track_visibility='onchange')
    exit_id = fields.Many2one('hr.exit')
    responsible_user_id = fields.Many2one('res.users', string='Responsible User', required=True)
    user_id = fields.Many2one(related="exit_id.user_id", string="User", type='many2one', relation='res.users', \
                              readonly=True, store=True)
    checklist_line_ids = fields.Many2many('hr.exit.checklist.line',
                                          'rel_exit_checklist_line', 'exit_line_id', 'checklist_exit_line_id',
                                          string='Checklist Lines')

    @api.onchange('checklist_id')
    def get_checklistline(self):
        self.checklist_line_ids = self.checklist_id.checklist_line_ids

    def checklist_confirm(self):
        self.state = 'confirm'

    def checklist_approved(self):
        self.state = 'approved'

    def checklist_cancel(self):
        self.state = 'cancel'

    def checklist_reject(self):
        self.state = 'reject'


class hr_exit(models.Model):
    _name = 'hr.exit'
    _description = "Exit"
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    employee_id = fields.Many2one('hr.employee', required=True, string="Employee")
    request_date = fields.Date('Request Date', readonly='1',
                               default=fields.datetime.now())
    user_id = fields.Many2one('res.users', string='User',
                              default=lambda self: self.env.user,
                              states={'draft': [('readonly', False)]}, readonly=True)
    confirm_date = fields.Date(string='Confirm Date(Employee)',
                               readonly=True, copy=False)
    dept_approved_date = fields.Date(string='Approved Date(Department Manager)',
                                     readonly=True, copy=False)
    validate_date = fields.Date(string='Approved Date(HR Manager)',
                                readonly=True, copy=False)
    general_validate_date = fields.Date(string='Approved Date(General Manager)',
                                        readonly=True, copy=False)
    confirm_by_id = fields.Many2one('res.users', string='Confirm By', readonly=True, copy=False)
    dept_manager_by_id = fields.Many2one('res.users', string='Approved By Department Manager', readonly=True,
                                         copy=False)
    hr_manager_by_id = fields.Many2one('res.users', string='Approved By HR Manager', readonly=True, copy=False)
    gen_man_by_id = fields.Many2one('res.users', string='Approved By General Manager', readonly=True, copy=False)
    reason_for_leaving = fields.Char(string='Reason For Leaving', required=True, copy=False, readonly=True)
    last_work_date = fields.Date(string='Last Day of Work')
    survey = fields.Many2one('survey.survey', string="Interview", readonly=True)
    # response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null", oldname="response")
    partner_id = fields.Many2one('res.partner', "Contact", readonly=True)

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('approved_dept_manager', 'Approved by Dept Manager'),
        ('approved_hr_manager', 'Approved by HR Manager'),
        ('approved_general_manager', 'Approved by General Manager'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ('reject', 'Rejected')], string='State',
        readonly=True, help='', default='draft',
        track_visibility='onchange')
    notes = fields.Text(string='Notes')
    manager_id = fields.Many2one('hr.employee', 'Department Manager',
                                 related='employee_id.department_id.manager_id',
                                 states={'draft': [('readonly', False)]}, readonly=True, store=True,
                                 help='This area is automatically filled by the user who \
                        will confirm the exit', copy=False)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    department_id = fields.Many2one(related='employee_id.department_id',
                                    string='Department', type='many2one', relation='hr.department',
                                    readonly=True, store=True)
    job_id = fields.Char(related='employee_id.job_title', string='Job Title', readonly=True, store=True)
    checklist_ids = fields.One2many('hr.exit.line', 'exit_id', string="Checklist")
    contract_id = fields.Char(related='employee_id.contract_id.name', string='Contract', readonly=False)
    contract_id_name = fields.Char(related='employee_id.contract_id.name', string='Contract', readonly=False)
    contract_ids = fields.Many2many('hr.contract', 'hr_contract_contract_tag')

    def action_makeMeeting(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        #         self.ensure_one()
        #         partners = self.partner_id | self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id

        #         category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window'].for_xml_id('calendar', 'action_calendar_event')
        #         res['context'] = {
        #             'search_default_partner_ids': self.partner_id.name,
        #             'default_partner_ids': partners.ids,
        #             'default_user_id': self.env.uid,
        #             'default_name': self.name,
        #             'default_categ_ids': category and [category.id] or False,
        #         }
        return res

    # ~ @api.multi
    # ~ def action_start_survey(self):
    # ~ self.ensure_one()
    # ~ if not self.response_id:
    # ~ response = self.env['survey.user_input'].create({'survey_id': self.survey.id, 'partner_id': self.partner_id.id})
    # ~ self.response_id = response.id
    # ~ else:
    # ~ response = self.response_id
    # ~ return self.survey.with_context(survey_token=response.token).action_start_survey()

    # ~ @api.multi
    # ~ def action_print_survey(self):
    # ~ """ If response is available then print this response otherwise print survey form (print template of the survey) """
    # ~ self.ensure_one()
    # ~ if not self.response_id:
    # ~ return self.survey.action_print_survey()
    # ~ else:
    # ~ response = self.response_id
    # ~ return self.survey.with_context(survey_token=response.token).action_print_survey()

    def get_contract_latest(self, employee, date_from, date_to):
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        contract_obj = self.env['hr.contract']
        clause = []
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), '|', '|'] + clause_1 + clause_2 + clause_3
        contract_ids = contract_obj.search(clause_final, limit=1)
        return contract_ids

    @api.onchange('employee_id', 'state')
    def get_contract(self):
        contract_obj = self.env['hr.contract']
        self.partner_id = self.employee_id.address_home_id.id
        all_contract_ids = contract_obj.search([('employee_id', '=', self.employee_id.id)])
        contract_ids = self.get_contract_latest(self.employee_id, self.request_date, self.request_date)
        if contract_ids:
            self.contract_id = contract_ids[0].id
            self.contract_ids = all_contract_ids.ids

    def exit_approved_by_department(self):
        obj_emp = self.env['hr.employee']
        self.state = 'confirm'
        self.dept_approved_date = time.strftime('%Y-%m-%d')

    def request_set(self):
        self.state = 'draft'

    def exit_cancel(self):
        self.state = 'cancel'

    def get_confirm(self):
        self.state = 'confirm'
        self.confirm_date = time.strftime('%Y-%m-%d')
        self.confirm_by_id = self.env.user.id
        if self.state == 'confirm':
            template = self.env.ref('hr_exit_process.employee_exit_confirm_process_mail_template', False)
            template.send_mail(self.id, force_send=True)

    def get_apprv_dept_manager(self):
        self.state = 'approved_dept_manager'
        self.dept_approved_date = time.strftime('%Y-%m-%d')
        self.dept_manager_by_id = self.env.user.id
        checklist_data = self.env['hr.exit.checklist'].search([])
        for checklist in checklist_data:
            vals = {'checklist_id': checklist.id,
                    'exit_id': self.id,
                    'employee_id': self.employee_id.id,
                    'state': 'confirm',
                    'responsible_user_id': checklist.responsible_user_id.id,
                    'checklist_line_ids': [(6, 0, checklist.checklist_line_ids.ids)]}
            self.env['hr.exit.line'].create(vals)
        if self.state == 'approved_dept_manager':
            template = self.env.ref('hr_exit_process.employee_exit_approved_process_mail_template', False)
            # template.write(
            #     {
            #         'subject': ' Employee Exit Process Approve Request Notification',
            #         'email_from': self.env.user.email,
            #         'email_to': self.manager_id.work_email,
            #         'email_cc': self.employee_id.coach_id.work_email})
            template.send_mail(self.id, force_send=True)

    def get_apprv_hr_manager(self):
        self.state = 'approved_hr_manager'
        self.validate_date = time.strftime('%Y-%m-%d')
        self.hr_manager_by_id = self.env.user.id
        for record in self.checklist_ids:
            if not record.state in ['approved']:
                raise ValidationError(
                    _('You can not approved this request since there are some checklist to be approved by respected department'))
        if self.state == 'approved_hr_manager':
            template = self.env.ref('hr_exit_process.employee_exit_approved_two_process_mail_template', False)
            template.send_mail(self.id, force_send=True)

    def get_apprv_general_manager(self):
        self.state = 'approved_general_manager'
        self.general_validate_date = time.strftime('%Y-%m-%d')
        self.gen_man_by_id = self.env.user.id
        if self.state == 'approved_general_manager':
            template = self.env.ref('hr_exit_process.employee_exit_approved_general_manager_process_mail_template',
                                    False)
            template.send_mail(self.id, force_send=True)

    def get_done(self):
        for record in self:
            record.state = 'done'
            record.employee_id.write({'state': 'exit'})
            record.employee_id.contract_id.write({'state': 'exit'})

    def get_reject(self):
        if self.state == 'approved_dept_manager':
            template = self.env.ref('hr_exit_process.employee_exit_reject_mail_template', False)
            template.send_mail(self.id, force_send=True)

        if self.state == 'approved_hr_manager':
            template = self.env.ref('hr_exit_process.employee_exit_reject__two_mail_template', False)
            template.send_mail(self.id, force_send=True)

        self.state = 'reject'


class Employee(models.Model):
    _inherit = 'hr.employee'

    state = fields.Selection(selection=[
        ('draft', 'Enroll'),
        ('exit', 'Exit')], string='State',
        readonly=True, help='', default='draft',
        track_visibility='onchange')


class Contract(models.Model):
    _inherit = 'hr.contract'

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('exit', 'Exit'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', copy=False,
        tracking=True, help='Status of the contract', default='draft')
