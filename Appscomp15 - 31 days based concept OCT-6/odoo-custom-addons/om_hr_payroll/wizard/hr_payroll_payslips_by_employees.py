# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning, ValidationError, UserError


class HrPayslipEmployees(models.TransientModel):
    _name = 'hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees')

    # current_month = fields.Char(string="Month")

    def compute_sheet(self):
        self.payslip_validate()
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
                'company_id': employee.company_id.id,
            }
            payslips += self.env['hr.payslip'].create(res)
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}

    def payslip_validate(self):
        from datetime import datetime
        currentMonth = datetime.now().month
        import datetime
        date = datetime.datetime.now().month
        date_mon = datetime.datetime(1, int(date), 1).strftime("%B")
        payslip_records = self.env['hr.payslip'].search(
            [('employee_id', '=', self.employee_ids.ids)])
        for pay in payslip_records:
            # if pay.employee_id.name == self.employee_ids.name and pay.date_months == date_mon:
            #     raise ValidationError(_('Alert!,The Selected Employee of Mr." %s"  Already The payslip has generated \n'
            #                             'and The Payslip can only be generated once.') % self.employee_ids.name)
            if self.employee_ids:
                for batch_employee in self.employee_ids:
                    if pay.employee_id.name == batch_employee.name and pay.date_months == date_mon:
                        raise ValidationError(_('Alert!,The Selected Employee, Already The payslip has generated \n'
                                                'and The Payslip can only be generated once.'))
