from odoo import models, fields, api, _
import xlwt
from io import BytesIO
import base64
import itertools
from operator import itemgetter
from odoo.exceptions import Warning
from odoo import tools
from xlwt import easyxf
import datetime
from odoo.exceptions import UserError
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, ValidationError, UserError
import pdb

cell = easyxf('pattern: pattern solid, fore_colour yellow')
ADDONS_PATH = tools.config['addons_path'].split(",")[-1]

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'),
              ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'),
              ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'),
              ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')]


class HrPayRollExcelReport(models.TransientModel):
    _name = 'hr.payroll.excel.report.wizard'
    _description = 'Hr PayRoll Excel Report'

    start_date = fields.Datetime('Start date')
    end_date = fields.Datetime('End date')
    attachment = fields.Binary('File')
    attach_name = fields.Char('Attachment Name')
    summary_file = fields.Binary('Fleet Vehicle  Usage Report')
    file_name = fields.Char('File Name')
    report_printed = fields.Boolean('Fleet Vehicle  Usage Report')
    current_time = fields.Date('Current Time', default=lambda self: fields.Datetime.now())
    ams_time = datetime.now() + timedelta(hours=5, minutes=30)
    date = ams_time.strftime('%d-%m-%Y %H:%M:%S')
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    employee_id = fields.Many2many('hr.employee', string='Employee')
    person_count = fields.Integer(string="Person Count", default=0)
    department_id = fields.Many2many('hr.department', string='Department')
    employee_boolean = fields.Boolean('All Employee')
    salary_strut_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')

    by_month_year = fields.Boolean('By Month Year')
    by_date_range = fields.Boolean('By Date Range ')
    by_date_range_year_month = fields.Selection([
        ('by_month_year', 'By Month/Year'),
    ], string="Select Period Type", default='by_month_year')
    selct_month = fields.Selection([
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
    ], string="Month/Year")

    # month_master = fields.Many2one('hr.payroll.month', string='Month/Year')
    year_master = fields.Many2one('hr.payroll.year', string='Year')

    @api.onchange('employee_id')
    def count_employees(self):
        for employee in self:
            employee.person_count = len(self.employee_id)

    def action_get_hr_payroll_excel_report(self):
        workbook = xlwt.Workbook()
        worksheet1 = workbook.add_sheet('HR Payroll Excel Report')

        design_6 = easyxf('align: horiz left;font: bold 1;')
        design_7 = easyxf('align: horiz center;font: bold 1;')
        design_8 = easyxf('align: horiz left;')
        design_9 = easyxf('align: horiz right;')
        design_10 = easyxf('align: horiz right; pattern: pattern solid, fore_colour red;')
        design_11 = easyxf('align: horiz right; pattern: pattern solid, fore_colour green;')
        design_12 = easyxf('align: horiz right; pattern: pattern solid, fore_colour gray25;')
        design_13 = easyxf('align: horiz center;font: bold 1;pattern: pattern solid, fore_colour gray25;')

        worksheet1.col(0).width = 2000
        worksheet1.col(1).width = 6000
        worksheet1.col(2).width = 4500
        worksheet1.col(3).width = 4500
        worksheet1.col(4).width = 6000
        worksheet1.col(5).width = 4500
        worksheet1.col(6).width = 4000
        worksheet1.col(7).width = 4000
        worksheet1.col(8).width = 3000
        worksheet1.col(9).width = 3000
        worksheet1.col(10).width = 3000
        worksheet1.col(11).width = 3000
        worksheet1.col(12).width = 3500
        worksheet1.col(13).width = 3000
        worksheet1.col(14).width = 3000
        worksheet1.col(15).width = 3000
        worksheet1.col(16).width = 3000
        worksheet1.col(17).width = 3000
        worksheet1.col(18).width = 3000
        worksheet1.col(19).width = 3000

        rows = 0
        cols = 0
        row_pq = 4
        col_pq = 5

        worksheet1.set_panes_frozen(True)
        worksheet1.set_horz_split_pos(rows + 1)

        from datetime import date, timedelta
        import calendar
        import datetime
        start_day_of_current_month = date.today().replace(day=1)
        last_day_of_current_month = date.today() + relativedelta(day=31)
        rec_id = self.sudo().create({'start_date': start_day_of_current_month, 'end_date': last_day_of_current_month})

        start_date = self.start_date
        end_date = self.end_date
        import datetime
        domain = [
            ('employee_id', '=', self.employee_id.ids),
            ('date_from', '=', self.start_date),
            ('date_to', '=', self.end_date)
        ]
        domain1 = [
            ('employee_id', '=', self.employee_id.ids),
            ('date_months', '=', self.selct_month),
            ('date_year', '=', self.year_master.name)
        ]

        domain4 = [
            ('struct_id', '=', self.salary_strut_id.ids),
            ('date_months', '=', self.selct_month),
            ('date_year', '=', self.year_master.name)
        ]

        domain2 = [
            ('employee_id.department_id', '=', self.department_id.ids),
            ('date_months', '=', self.selct_month),
            ('date_year', '=', self.year_master.name)
        ]

        domain3 = [
            ('date_months', '=', self.selct_month),
            ('date_year', '=', self.year_master.name)
        ]

        # domain5 = [
        #     ('employee_id.department_id', '=', self.department_id.ids),
        #     ('date_months', '=', self.selct_month),
        #     ('date_year', '=', self.year_master.name)
        # ]

        if not self.employee_id and not self.department_id and not self.salary_strut_id and self.selct_month and self.year_master:

            col_1 = 0
            rows += 1
            worksheet1.write_merge(rows, rows, 2, 6,
                                   'EMPLOYEE PAYROLL MONTHLY SUMMARY - %s - %s ' % (
                                       self.selct_month, self.year_master.name), design_13)
            rows += 1
            worksheet1.write(rows, 3, 'GENERATED BY', design_13)
            worksheet1.write(rows, 4, self.user_id.name, design_13)
            rows += 1
            if self.employee_boolean:
                worksheet1.write(rows, 3, ' ALL Employee', design_13)
                worksheet1.write(rows, 4, ' All Department', design_13)

            rows += 1
            worksheet1.write(rows, col_1, _('Sl.No'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('EMPLOYEE'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DEPARTMENT'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DATE OF JOINING'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DESIGNATION'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('BANK ACCOUNT'), design_13)
            col_1 += 1
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain3, order='date_from asc')
            salary_struc = self.env['hr.salary.rule'].sudo().search(
                [('active', '=',True)])

            for value in salary_struc:
                salary_line = []
                worksheet1.write(rows, col_1, value.code, design_13)
                # salary_line.append(a.code)
                col_1 += 1

            sl_no = 1
            row_pq = row_pq + 1
            col_pq = col_pq + 1
            mr_num = []
            res = []
            count = 0
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain3, order='date_from asc')
            if payroll:
                for record in payroll:
                    count += 1
                    if self.by_date_range_year_month == 'by_month_year':
                        if self.selct_month == record.date_months:

                            worksheet1.write(row_pq, 0, sl_no, design_7)
                            if record.employee_id.name:
                                worksheet1.write(row_pq, 1, record.employee_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 1, '-', design_7)
                            if record.employee_id.department_id.name:
                                worksheet1.write(row_pq, 2, record.employee_id.department_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 2, '-', design_7)
                            if record.employee_id.date_of_joining:
                                worksheet1.write(row_pq, 3, str(record.employee_id.date_of_joining), design_8)
                            else:
                                worksheet1.write(row_pq, 3, '-', design_7)
                            if record.employee_id.job_id.name:
                                worksheet1.write(row_pq, 4, record.employee_id.job_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 4, '-', design_7)
                            if record.employee_id.bank_account_id.acc_number:
                                worksheet1.write(row_pq, 5, record.employee_id.bank_account_id.acc_number, design_8)
                            else:
                                worksheet1.write(row_pq, 5, '-', design_7)

                            select_date_from = record.date_from
                            select_date_to = record.date_to
                            select_month_from = select_date_from.strftime("%B")
                            select_month_to = select_date_to.strftime("%B")
                            # payroll_cal = self.env['hr.payroll.structure'].sudo().sudo().search(domain3, order='date_from asc')
                            # for salary_line in payroll_cal:
                            salary_struct = self.env['hr.salary.rule'].sudo().search(
                                [('active', '=', True)])
                            for data in record.line_ids:
                                for struct in salary_struct:
                                    if data.code == struct.code:
                                        worksheet1.write(row_pq, col_pq,
                                                        str('%.2f' % data.amount) + ' ' + record.company_id.currency_id.name,
                                                        design_9)

                                    col_pq += 1
                                col_pq = 6
                            sl_no += 1
                            row_pq += 1
            else:
                raise ValidationError(_("Alert! The Selected Month & Year contains No Records."))

        elif self.employee_id and self.selct_month and self.year_master:
            col_1 = 0
            rows += 1
            worksheet1.write_merge(rows, rows, 2, 6,
                                   'EMPLOYEE PAYROLL MONTHLY SUMMARY - %s - %s ' % (
                                       self.selct_month, self.year_master.name), design_13)
            rows += 1
            worksheet1.write(rows, 3, 'GENERATED BY', design_13)
            worksheet1.write(rows, 4, self.user_id.name, design_13)
            rows += 1
            worksheet1.write(rows, col_1, _('Sl.No'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('EMPLOYEE'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DEPARTMENT'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DATE OF JOINING'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DESIGNATION'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('BANK ACCOUNT'), design_13)
            col_1 += 1
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain1, order='date_from asc')
            salary_struc = self.env['hr.salary.rule'].sudo().search(
                [('active', '=', True)])

            for value in salary_struc:
                salary_line = []
                worksheet1.write(rows, col_1, value.code, design_13)
                # salary_line.append(a.code)
                col_1 += 1

            sl_no = 1
            row_pq = row_pq + 1
            col_pq = col_pq + 1
            mr_num = []
            res = []
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain1, order='date_from asc')
            if payroll:
                for record in payroll:
                    if self.by_date_range_year_month == 'by_month_year':
                        if self.selct_month == record.date_months:
                            worksheet1.write(row_pq, 0, sl_no, design_7)
                            if record.employee_id.name:
                                worksheet1.write(row_pq, 1, record.employee_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 1, '-', design_7)
                            if record.employee_id.department_id.name:
                                worksheet1.write(row_pq, 2, record.employee_id.department_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 2, '-', design_7)
                            if record.employee_id.date_of_joining:
                                worksheet1.write(row_pq, 3, str(record.employee_id.date_of_joining), design_8)
                            else:
                                worksheet1.write(row_pq, 3, '-', design_7)
                            if record.employee_id.job_id.name:
                                worksheet1.write(row_pq, 4, record.employee_id.job_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 4, '-', design_7)
                            if record.employee_id.bank_account_id.acc_number:
                                worksheet1.write(row_pq, 5, record.employee_id.bank_account_id.acc_number, design_8)
                            else:
                                worksheet1.write(row_pq, 5, '-', design_7)

                            select_date_from = record.date_from
                            select_date_to = record.date_to
                            select_month_from = select_date_from.strftime("%B")
                            select_month_to = select_date_to.strftime("%B")
                            salary_struct = self.env['hr.salary.rule'].sudo().search(
                                [('active', '=', True)])
                            for data in record.line_ids:
                                for struct in salary_struct:
                                    if data.code == struct.code:
                                        worksheet1.write(row_pq, col_pq,
                                                         str('%.2f' % data.amount) + ' ' + record.company_id.currency_id.name,
                                                         design_9)

                                    col_pq += 1
                                col_pq = 6
                            sl_no += 1
                            row_pq += 1
            else:
                raise ValidationError(_("Alert! The Selected Month & Year contains No Records."))

        elif self.department_id and self.selct_month and self.year_master:
            col_1 = 0
            rows += 1
            worksheet1.write_merge(rows, rows, 2, 6,
                                   'EMPLOYEE PAYROLL MONTHLY SUMMARY - %s - %s ' % (
                                       self.selct_month, self.year_master.name), design_13)
            rows += 1
            worksheet1.write(rows, 3, 'GENERATED BY', design_13)
            worksheet1.write(rows, 4, self.user_id.name, design_13)
            rows += 1
            if self.department_id:
                worksheet1.write(rows, 4, '  Department', design_13)


            rows += 1
            worksheet1.write(rows, col_1, _('Sl.No'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('EMPLOYEE'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DEPARTMENT'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DATE OF JOINING'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DESIGNATION'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('BANK ACCOUNT'), design_13)
            col_1 += 1
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain2, order='date_from asc')
            salary_struc = self.env['hr.salary.rule'].sudo().search(
                [('active', '=', True)])
            for value in salary_struc:
                salary_line = []
                worksheet1.write(rows, col_1, value.code, design_13)
                # salary_line.append(a.code)
                col_1 += 1

            sl_no = 1
            row_pq = row_pq + 1
            col_pq = col_pq + 1
            mr_num = []
            res = []
            count = 0
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain2, order='date_from asc')
            if payroll:
                for record in payroll:
                    count += 1
                    if self.by_date_range_year_month == 'by_month_year':
                        if self.selct_month == record.date_months:

                            worksheet1.write(row_pq, 0, sl_no, design_7)
                            if record.employee_id.name:
                                worksheet1.write(row_pq, 1, record.employee_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 1, '-', design_7)
                            if record.employee_id.department_id.name:
                                worksheet1.write(row_pq, 2, record.employee_id.department_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 2, '-', design_7)
                            if record.employee_id.date_of_joining:
                                worksheet1.write(row_pq, 3, str(record.employee_id.date_of_joining), design_8)
                            else:
                                worksheet1.write(row_pq, 3, '-', design_7)
                            if record.employee_id.job_id.name:
                                worksheet1.write(row_pq, 4, record.employee_id.job_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 4, '-', design_7)
                            if record.employee_id.bank_account_id.acc_number:
                                worksheet1.write(row_pq, 5, record.employee_id.bank_account_id.acc_number, design_8)
                            else:
                                worksheet1.write(row_pq, 5, '-', design_7)

                            select_date_from = record.date_from
                            select_date_to = record.date_to
                            select_month_from = select_date_from.strftime("%B")
                            select_month_to = select_date_to.strftime("%B")
                            salary_struct = self.env['hr.salary.rule'].sudo().search(
                                [('active', '=', True)])
                            for data in record.line_ids:
                                for struct in salary_struct:
                                    if data.code == struct.code:
                                        worksheet1.write(row_pq, col_pq,
                                                         str('%.2f' % data.amount) + ' ' + record.company_id.currency_id.name,
                                                         design_9)

                                    col_pq += 1
                                col_pq = 6
                            sl_no += 1
                            row_pq += 1
            else:
                raise ValidationError(_("Alert! The Selected Month & Year contains No Records."))

        elif self.salary_strut_id and self.selct_month and self.year_master:
            row_pq = 5
            col_1 = 0
            rows += 1
            worksheet1.write_merge(rows, rows, 2, 6,
                                   'EMPLOYEE PAYROLL MONTHLY SUMMARY - %s - %s ' % (
                                       self.selct_month, self.year_master.name), design_13)
            rows += 1
            worksheet1.write(rows, 3, 'GENERATED BY', design_13)
            worksheet1.write(rows, 4, self.user_id.name, design_13)
            rows += 1
            worksheet1.write(rows, 3, 'Salary Structure', design_13)
            worksheet1.write(rows, 4, self.salary_strut_id.name, design_13)
            rows += 2
            worksheet1.write(rows, col_1, _('Sl.No'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('EMPLOYEE'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DEPARTMENT'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DATE OF JOINING'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('DESIGNATION'), design_13)
            col_1 += 1
            worksheet1.write(rows, col_1, _('BANK ACCOUNT'), design_13)
            col_1 += 1
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain4, order='date_from asc')
            for value in payroll:
                salary_struc = self.env['hr.payroll.structure'].sudo().search(
                    [('name', '=', value.struct_id.name)])
                total = 0
                salary_line = []
                for a in salary_struc.rule_ids:
                    worksheet1.write(rows, col_1, a.code, design_13)
                    salary_line.append(a.code)
                    col_1 += 1
                break
            sl_no = 1
            row_pq = row_pq + 1
            col_pq = col_pq + 1
            mr_num = []
            res = []
            count = 0
            payroll = self.env['hr.payslip'].sudo().sudo().search(domain4, order='date_from asc')
            if payroll:
                for record in payroll:
                    count += 1
                    if self.by_date_range_year_month == 'by_month_year':
                        if self.selct_month == record.date_months:

                            worksheet1.write(row_pq, 0, sl_no, design_7)
                            if record.employee_id.name:
                                worksheet1.write(row_pq, 1, record.employee_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 1, '-', design_7)
                            if record.employee_id.department_id.name:
                                worksheet1.write(row_pq, 2, record.employee_id.department_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 2, '-', design_7)
                            if record.employee_id.date_of_joining:
                                worksheet1.write(row_pq, 3, str(record.employee_id.date_of_joining), design_8)
                            else:
                                worksheet1.write(row_pq, 3, '-', design_7)
                            if record.employee_id.job_id.name:
                                worksheet1.write(row_pq, 4, record.employee_id.job_id.name, design_8)
                            else:
                                worksheet1.write(row_pq, 4, '-', design_7)
                            if record.employee_id.bank_account_id.acc_number:
                                worksheet1.write(row_pq, 5, record.employee_id.bank_account_id.acc_number, design_8)
                            else:
                                worksheet1.write(row_pq, 5, '-', design_7)

                            select_date_from = record.date_from
                            select_date_to = record.date_to
                            select_month_from = select_date_from.strftime("%B")
                            select_month_to = select_date_to.strftime("%B")
                            for data in record.line_ids:
                                if data.amount > 0:
                                    worksheet1.write(row_pq, col_pq,
                                                     str('%.2f' % data.amount) + ' ' + record.company_id.currency_id.name,
                                                     design_9)
                                else:
                                    worksheet1.write(row_pq, col_pq,
                                                     '-',
                                                     design_7)
                                col_pq += 1
                            col_pq = 6
                            sl_no += 1
                            row_pq += 1
            else:
                raise ValidationError(_("Alert! The Selected Month & Year contains No Records."))

        fp = BytesIO()
        o = workbook.save(fp)
        fp.read()
        excel_file = base64.b64encode(fp.getvalue())
        self.write({'summary_file': excel_file, 'file_name': 'HR Payroll Excel Report - [ %s ].xls' % self.date,
                    'report_printed': True})
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'hr.payroll.excel.report.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }
