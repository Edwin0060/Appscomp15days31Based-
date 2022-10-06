# -*- coding: utf-8 -*-
# import psutil
from odoo import models, fields, api, _
from datetime import timedelta, date, datetime
from odoo.tools import float_compare, float_round, float_repr

from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


def time_to_float(t):
    return float_round(t.hour + t.minute / 60 + t.second / 3600, precision_digits=2)


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    parent_id = fields.Many2one(related='employee_id.parent_id', string='Reporting Head')
    employee_work_hour_time = fields.Float(string="Diff Hour's")
    total_work_hour_time = fields.Float(string="Office Hour's", compute='_compute_employee_check_in')
    checkin_time = fields.Float(string="Check in Time", compute='_compute_check_in_time')
    checkout_time = fields.Float(string="Check Out Time")
    employee_checkin_time = fields.Float(string="Office Check In", compute='_compute_check_in_time')
    employee_checkout_time = fields.Float(string="Office Check Out")
    diff_check_in_time = fields.Float(string="Late Comer's")
    diff_check_out_time = fields.Float(string="Early Go")
    mac_addreass = fields.Char(string="Check In Mac ID")
    mac_check_out_addreass = fields.Char(string="Check Out Mac ID")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        print(self.env.context)
        if 'team_attendance' in self.env.context and self.env.context['team_attendance']:
            res_user = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
            emp_id = self.env['hr.employee'].search([('user_id', '=', res_user.id)])
            # if len(emp_id) == 1:
            if self.env.user.has_group('asppscomp_hr.group_employee_team_leader'):
                args += [('parent_id', '=', emp_id.id)]
            # ~ if res_user.system_admin:
            # ~ args += [('id', '!=', 1)]
            # ~ else:
            # ~ args += [('id', '=', self._uid)]
        return super(HrAttendance, self).search(args, offset, limit, order, count=count)

    @api.depends('total_work_hour_time')
    @api.onchange('employee_id', 'check_out', 'check_in')
    def _compute_employee_check_in(self):
        for rec in self:
            if rec.employee_id and rec.total_work_hour_time == 0:
                check_in_dates = timedelta(hours=rec.employee_id.hour, minutes=rec.employee_id.minute)
                check_out_dates = timedelta(hours=rec.employee_id.check_out_hour,
                                            minutes=rec.employee_id.check_out_minute)
                total_date = check_out_dates - check_in_dates
                attendance = total_date.total_seconds() / 3600.0
                final_string = str('%.2f' % attendance)
                rec.total_work_hour_time = final_string
                # currentDate = datetime.now() + timedelta(hours=5, minutes=30)
                # dfi  = currentDate.strftime('%H:%M:%S')
                # chek_in_time = rec.check_in.time()

    @api.depends('checkin_time', 'employee_checkin_time', 'employee_checkout_time', 'checkout_time')
    @api.onchange('employee_id', 'check_out', 'check_in', 'employee_checkin_time')
    def _compute_check_in_time(self):
        # import getmac
        for rec in self:
            if rec.employee_id and rec.check_in and rec.checkin_time == 0 and rec.employee_checkin_time == 0:
                employee_minute_add = rec.employee_id.minute + 15
                # employee_minute_add = rec.employee_id.minute
                float_time = float_round(rec.employee_id.hour + employee_minute_add / 60, precision_digits=2)
                rec.employee_checkin_time = float_time
                attendance_hour_diff = rec.check_in + timedelta(hours=5, minutes=30)
                float_check_time = float_round(attendance_hour_diff.hour + attendance_hour_diff.minute / 60,
                                               precision_digits=2)
                rec.checkin_time = float_check_time
                differnt_check_hour = rec.checkin_time - rec.employee_checkin_time
                rec.diff_check_in_time = str('%.2f' % differnt_check_hour)
                # rec.mac_addreass = getmac.get_mac_address()

            if rec.employee_id and rec.check_out and rec.employee_checkout_time == 0 and rec.checkout_time == 0:
                employee_check_out_minute_add = rec.employee_id.check_out_minute - 15
                # employee_check_out_minute_add = rec.employee_id.check_out_minute
                float_time_checkout = float_round(rec.employee_id.check_out_hour + employee_check_out_minute_add / 60,
                                                  precision_digits=2)
                rec.employee_checkout_time = float_time_checkout
                attendance_hour_check_out_diff = rec.check_out + timedelta(hours=5, minutes=30)
                float_check_out_time = float_round(
                    attendance_hour_check_out_diff.hour + attendance_hour_check_out_diff.minute / 60,
                    precision_digits=2)
                rec.checkout_time = float_check_out_time
                # differnt_check_out_hour = rec.checkout_time - rec.employee_checkout_time
                # rec.diff_check_out_time = str('%.2f' % differnt_check_out_hour)
                # rec.mac_check_out_addreass = getmac.get_mac_address()
                if rec.checkout_time <= rec.employee_checkout_time:
                    differnt_check_out_hour = rec.checkout_time - rec.employee_checkout_time
                    rec.diff_check_out_time = str('%.2f' % differnt_check_out_hour)

            if rec.worked_hours == rec.total_work_hour_time:
                duration = 0.00
            else:
                duration = rec.worked_hours - rec.total_work_hour_time
                # duration = rec.worked_hours == rec.total_work_hour_time
                rec.employee_work_hour_time = duration
