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
import pdb

cell = easyxf('pattern: pattern solid, fore_colour yellow')
ADDONS_PATH = tools.config['addons_path'].split(",")[-1]

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'),
              ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'),
              ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'),
              ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')]


class EmployeeTimesheetReport(models.TransientModel):
    _name = 'employee.timesheet.report.wizard'

    employee_id = fields.Many2one('hr.employee', string="Employee ")
    leave_id = fields.Many2one('leave.description.master', string="Leave Type")
    date_start = fields.Date(string="Date From", required=True)
    date_end = fields.Date(string="Date To", required=True)
    leave_type = fields.Many2one('hr.leave.type', string="leave Types")
    attachment = fields.Binary('File')
    summary_file = fields.Binary('Employee Timesheet Statement')
    file_name = fields.Char('File Name')
    report_printed = fields.Boolean('Purchase Backorder Report')
    ams_time = datetime.now() + timedelta(hours=5, minutes=30)
    date = ams_time.strftime('%d-%m-%Y %H:%M:%S')
    # user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    partner = fields.Boolean(string="Partner")

    def time_between(self):
        # start_date = date(self.date_start)
        # end_date = date(self.date_end)
        delta = self.date_end - self.date_start
        for i in range(delta.days + 1):
            day = self.date_start + timedelta(days=i)
            date_day = day
            print(day)

    def action_employee_timesheet_report_wizard_excel(self):
        workbook = xlwt.Workbook()
        worksheet1 = workbook.add_sheet('Employee Timesheet Report')
        design_6 = easyxf('align: horiz left;font: bold 1;')
        design_7 = easyxf('align: horiz center;font: bold 1;')
        design_8 = easyxf('align: horiz left;')
        design_9 = easyxf('align: horiz right;')
        design_10 = easyxf('align: horiz right; pattern: pattern solid, fore_colour red;')
        design_11 = easyxf('align: horiz right; pattern: pattern solid, fore_colour green;')
        design_12 = easyxf('align: horiz right; pattern: pattern solid, fore_colour gray25;')
        design_13 = easyxf('align: horiz center;font: bold 1;pattern: pattern solid, fore_colour gray25;')

        worksheet1.col(0).width = 1600
        worksheet1.col(1).width = 5000
        worksheet1.col(2).width = 10000
        worksheet1.col(3).width = 6000
        worksheet1.col(4).width = 5500
        worksheet1.col(5).width = 3800
        worksheet1.col(6).width = 3000
        worksheet1.col(7).width = 3000
        worksheet1.col(8).width = 2800
        worksheet1.col(9).width = 3500
        worksheet1.col(10).width = 3500
        worksheet1.col(11).width = 5000

        rows = 0
        cols = 0
        row_pq = 5

        worksheet1.set_panes_frozen(True)
        worksheet1.set_horz_split_pos(rows + 1)
        worksheet1.set_remove_splits(True)

        col_1 = 0
        worksheet1.write_merge(rows, rows, 2, 6, 'EMPLOYEE TIMESHEET REPORT', design_13)
        rows += 1
        worksheet1.write(rows, 3, 'FROM', design_7)
        worksheet1.write(rows, 4, self.date_start.strftime('%d-%m-%Y'), design_7)
        rows += 1
        worksheet1.write(rows, 3, 'TO', design_7)
        worksheet1.write(rows, 4, self.date_end.strftime('%d-%m-%Y'), design_7)
        rows += 2
        worksheet1.write(rows, col_1, _('Sl.No'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Date of Timesheet'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Employee Name'), design_13)
        col_1 += 1
        worksheet1.write(rows, col_1, _('Department'), design_13)
        col_1 += 1

        sl_no = 1
        row_pq = row_pq + 1

        for record in self:
            domain = [('date', '>=', record.date_start), ('date', '<=', record.date_end),]
            employee_statement = self.env['account.analytic.line'].search(domain, order='employee_id asc, date asc')
            for timesheet in employee_statement:
                ref_date1 = timesheet.date
                import datetime
                d11 = str(ref_date1)
                dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d')
                date1 = dt21.strftime("%d/%m/%Y")
                worksheet1.write(row_pq, 0, sl_no, design_8)
                worksheet1.write(row_pq, 1, date1, design_8)
                worksheet1.write(row_pq, 2, timesheet.employee_id.display_name, design_8)
                if timesheet.employee_id.department_id:
                    worksheet1.write(row_pq, 3, timesheet.employee_id.department_id.name, design_8)
                else:
                    worksheet1.write(row_pq, 3, 'NIL', design_8)
                delta = self.date_end - self.date_start
                for i in range(delta.days + 1):
                    day = self.date_start + timedelta(days=i)
                    date_day = day
                    print(day)
                    # worksheet1.write(col_pq, 7, date_day, design_9)
                    worksheet1.write(rows, col_1, _(date_day), design_13)
                    col_1 += 1

                sl_no += 1
                row_pq += 1

        fp = BytesIO()
        o = workbook.save(fp)
        fp.read()
        excel_file = base64.b64encode(fp.getvalue())
        self.write({'summary_file': excel_file,
                    'file_name': 'Employee Timesheet Report-.[ %s ].xls' % self.date,
                    'report_printed': True})
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'employee.timesheet.report.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }
