# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo.exceptions import Warning, ValidationError, UserError
from odoo import api, fields, models, _


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',
        help="Defines the frequency of the wage payment.")
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule.")
    ctc = fields.Float(string='CTC', store=True)
    manual_ctc = fields.Float(string='CTC', store=True)
    wage = fields.Float(string='Basic')
    convenyance_allowance = fields.Float(string='Coveyance Allowance')
    special_allowance = fields.Float(string='Special Allowance')
    house_rent_allowance = fields.Float(string='House Rent Allowance')
    notice_period_pay = fields.Float(string='Notice Period Pay')
    leave_incentives = fields.Float(string='Leave Allowance')
    travel_incentives = fields.Float(string='Travel Allowance')
    health_insurance = fields.Float(string='Health Insurance')
    advance_salary = fields.Float(string="Advance Salary")
    loan_deduction = fields.Float(string="Loan Deduction")
    unpaid_leave_amount_deduction = fields.Float(string="Unpaid Amount Deduction")
    basic_percentage = fields.Float(string='Basic Percentage %')
    pf_basic_percentage = fields.Float(string='PF Percentage %')
    pf_basic_percentage_second = fields.Float(string='PF Percentage %')
    conveyence_percentage = fields.Float(string='Coveyance Allowance Percentage %')
    travel_percentage = fields.Float(string='Travel Allowance Percentage %')
    hra_percentage = fields.Float(string='HRA Allowance Percentage %')
    special_alwnance_percentage = fields.Float(string='Special Allowance Percentage %')
    house_allowance = fields.Float(string="HRA Allowance")
    pf_deduction = fields.Float(string="PF Deductions")
    pf_deduction_second = fields.Float(string="PF Deductions")
    basic_allowance = fields.Float(string="Basic Allowance")
    tds = fields.Float(string='TDS')
    professional_tax = fields.Float(string='Professional Tax')
    # esi = fields.Float(string='ESI', compute='_esi_calculation')
    esi = fields.Float(string='ESI')
    esi_second = fields.Float(string='ESI')
    weekly_incentive = fields.Float(string="Weekly Incentive")
    monthly_incentive = fields.Float(string="Monthly Incentive")
    special_incentive = fields.Float(string="Special Incentive")
    pf_amount = fields.Float(string="PF")
    pf_amount_second = fields.Float(string="PF")
    esi_basic_percentage = fields.Float(string='ESI Percentage %')
    esi_basic_percentage_second = fields.Float(string='ESI Percentage %')
    pf_type = fields.Selection([
        ('dynamic', 'Dynamic'),
        ('fix', 'Fixed'),
    ], string="PF Type", default="fix")
    salary_hike_effective_date = fields.Date(string="Salary Hike Effective Date")
    contract_amount_settlement = fields.Float(string='Contract Allowance Amount')
    contract_deduction_settlement = fields.Float(string='Contract Deduction Amount')
    # amount_settlment_diff = fields.Float(string='CTC Difference', compute='_onchange_amount_settlment_diff')
    amount_settlment_diff = fields.Float(string='CTC Difference')
    compute_contract_valdiate = fields.Boolean(string='Compute Contract')
    is_employee_salary_editable = fields.Boolean(string='Is Employee Salary Editable?',
                                                compute='_onchange_employee_salary_editable', store=True)
    current_employee = fields.Char(string='Employee  User', compute='_onchange_employee_user')
    approved_by = fields.Many2one('res.users', compute='_get_current_user', string='Current User')
    salary_hike_enabled = fields.Boolean(string='Salary Hike?')
    start_date_doj = fields.Date(string="Start Date",related='employee_id.date_of_joining')


    def _get_current_user(self):
        for rec in self:
            rec.approved_by = self.env.user

    @api.depends('approved_by', 'employee_id')
    @api.onchange('approved_by', 'employee_id')
    def _onchange_employee_user(self):
        self.current_employee = self.employee_id.user_id.name

    @api.onchange('ctc', 'manual_ctc')
    def _onchange_employee_ctc_to_manaual_ctc(self):
        if self.employee_id:
            self.ctc = self.manual_ctc

    @api.depends('is_employee_salary_editable', 'employee_id')
    @api.onchange('is_employee_salary_editable', 'employee_id')
    def _onchange_employee_salary_editable(self):
        if self.employee_id:
            hr_contract_manager = self.env.user.has_group('om_hr_payroll.group_emp_contract_access')
            if hr_contract_manager != self.employee_id.user_id.name:
                self.write({'is_employee_salary_editable': False})
            elif hr_contract_manager == self.employee_id.user_id.name:
                self.write({'is_employee_salary_editable': True})


    def clear_contract_amount_setup(self):
        for contract in self:
            if contract.ctc:
                contract.amount_settlment_diff = contract.ctc
                contract.wage = 0.00
                contract.basic_percentage = 0.00
                contract.tds = 0.00
                # contract.amount_settlment_diff = 0.00
                contract.professional_tax = 0.00
                contract.esi = 0.00
                contract.esi_second = 0.00
                contract.esi_basic_percentage = 0.00
                contract.esi_basic_percentage_second = 0.00
                contract.pf_type = False
                contract.pf_basic_percentage = 0.00
                contract.pf_basic_percentage_second = 0.00
                contract.hra_percentage = 0.00
                contract.house_rent_allowance = 0.00
                contract.convenyance_allowance = 0.00
                contract.special_allowance = 0.00
                contract.travel_incentives = 0.00
                contract.health_insurance = 0.00


    @api.depends('amount_settlment_diff')
    @api.onchange('amount_settlment_diff', 'wage', 'house_rent_allowance',
                  'convenyance_allowance', 'special_allowance',
                  'travel_incentives', 'health_insurance', 'contract_amount_settlement',
                  'tds','professional_tax', 'esi', 'esi_second')
    def _onchange_amount_settlment_diff(self):
        total_calculation = 0.00
        if self.ctc:
            self.contract_amount_settlement = self.wage + \
                                              self.house_rent_allowance + \
                                              self.convenyance_allowance + \
                                              self.special_allowance + \
                                              self.travel_incentives + \
                                              self.health_insurance
            self.contract_deduction_settlement = self.esi + \
                                                 self.esi_second + \
                                                 self.tds + \
                                                 self.professional_tax
            total_calculation = self.contract_amount_settlement + self.contract_deduction_settlement
            self.amount_settlment_diff = self.ctc - total_calculation


    def employee_contract_setup_validate(self):
        if self.employee_id:
            if self.amount_settlment_diff != 0.00 or self.amount_settlment_diff == 0.00 and self.wage == 0.00:
                raise ValidationError(
                    _("Alert!, Contract cannot be Validate for Mr.%s, "
                      "and The Contract Salary Allocation is Not Matching with CTC - %s. "
                      "and The Payment Difference is %s.") % (
                        self.employee_id.name, self.ctc,
                        self.amount_settlment_diff))
            else:
                self.write({'compute_contract_valdiate': True})

    def employee_salary_update(self):
        for salary in self:
            employee_hike_salary = []
            if salary.employee_id:
                if salary.employee_id.salary_revision_ids:
                    for hike in salary.employee_id.salary_revision_ids:
                        employee_hike_salary = hike.new_salary_amount
                        employee_hike_date = hike.new_salary_from
                    salary.write({
                        'ctc': employee_hike_salary,
                        'salary_hike_effective_date': employee_hike_date,
                        'salary_hike_enabled': True
                    })
                    salary.hra_allowance()
                else:
                    raise ValidationError(
                        _("Alert!, The Selected Employee of 'Mr.%s ', "
                          "Doesn't have any Salary Revisions or not mentioned,"
                          "System will Accept only the mentioned The CTC Amount %s INR.") % (
                            self.employee_id.name, self.ctc))

    def leave_refuse(self):
        employee_contract = self.env['hr.leave.allocation'].search([('employee_id', '=', self.employee_id.id)])
        for emp in employee_contract:
            join_date = self.employee_id.date_of_joining
            join_month = join_date.month
            currentDay = datetime.now().day
            currentMonth = datetime.now().month
            if join_month == currentMonth:
                for leave in employee_contract:
                    leave.write({'state': 'refuse'})

    @api.onchange('pf_amount', 'pf_type', 'pf_basic_percentage', 'pf_amount_second',
                          'pf_basic_percentage_second', 'esi_basic_percentage')
    def pf_type_amount(self):
        if self.pf_type == 'dynamic' and self.pf_basic_percentage <= 0 and self.pf_basic_percentage_second <= 0:
           self.pf_amount = False
           self.pf_amount_second = False
           self.pf_basic_percentage = False
        if self.pf_type != 'dynamic':
           self.pf_basic_percentage = False
           self.pf_basic_percentage_second = False

    # @api.onchange('date_start','employee_id')
    # def set_employee_doj_to_contract_date(self):
    #     if self.employee_id:
    #         self.date_start = self.employee_id.date_of_joining


    @api.onchange('wage', 'hra_percentage', 'basic_percentage',
                  'ctc', 'pf_basic_percentage', 'pf_amount',
                  'pf_type','esi','esi_basic_percentage','esi_second',
                  'esi_basic_percentage_second','pf_amount_second',
                  'pf_basic_percentage_second')
    def hra_allowance(self):
        for record in self:
            record.wage = False
            record.house_rent_allowance = False
            record.esi = False
            record.esi_second = False
            total_basic = 0.00
            total_conveyance = 0.00
            total_pf_deducions = 0.00
            total_esi = 0.00
            total_esi_second = 0.00
            total_pf_deducions_second = 0.00
            total_pf = 0.00
            if record.ctc:
                if record.basic_percentage:
                    total_basic = record.ctc * (1 - (record.basic_percentage or 0.0) / 100.0)
                    record.write({
                        'basic_allowance': total_basic})
                    record.wage = record.ctc - record.basic_allowance
            if record.wage > 0.00:
                if record.hra_percentage:
                    total_conveyance = record.wage * (1 - (record.hra_percentage or 0.0) / 100.0)
                    record.write({
                        'house_allowance': total_conveyance})
                    record.house_rent_allowance = record.wage - record.house_allowance
                if record.pf_basic_percentage and record.pf_type == 'dynamic':
                    total_pf_deducions = record.ctc * (1 - (record.pf_basic_percentage or 0.0) / 100.0)
                    total_pf_deducions_second = record.ctc * (1 - (record.pf_basic_percentage_second or 0.0) / 100.0)
                    record.write({
                        'pf_deduction': total_pf_deducions})
                    record.write({
                        'pf_deduction_second': total_pf_deducions_second})
                    record.pf_amount = record.ctc - record.pf_deduction
                    record.pf_amount_second = record.ctc - record.pf_deduction_second
            if record.ctc <= 21100.00:
                if record.ctc:
                    total_esi = (record.ctc * record.esi_basic_percentage) / 100.0
                    total_esi_second = (record.ctc * record.esi_basic_percentage_second) / 100.0
                    record.esi = total_esi
                    record.esi_second = total_esi_second
                else:
                    record.write({'esi':0.00,'esi_second':0.00})
            if record.ctc >= 15000.00 and record.pf_type != 'dynamic':
                if record.ctc:
                    total_pf = (1 * 1800)
                    record.pf_amount = total_pf
            if record.ctc >= 15000.00 and record.pf_type != 'dynamic':
                if record.ctc:
                    total_pf_second = (1 * 1800)
                    record.pf_amount_second = total_pf
            if record.ctc < 15000.00 and record.pf_type != 'dynamic':
                if record.ctc:
                    total_pf = (0 * 1800)
                    record.pf_amount = total_pf
            if record.ctc < 15000.00 and record.pf_type != 'dynamic':
                if record.ctc:
                    total_pf_second = (0 * 1800)
                    record.pf_amount_second = total_pf


    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0


class HrContractAdvantageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    lower_bound = fields.Float('Lower Bound', help="Lower bound authorized by the employer for this advantage")
    upper_bound = fields.Float('Upper Bound', help="Upper bound authorized by the employer for this advantage")
    default_value = fields.Float('Default value for this advantage')
