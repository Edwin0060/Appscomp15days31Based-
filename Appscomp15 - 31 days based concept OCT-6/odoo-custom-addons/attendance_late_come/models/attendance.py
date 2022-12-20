# -*- coding: utf-8 -*-
# import psutil
from odoo import models, fields, api, _
from datetime import timedelta, date, datetime
from odoo.tools import float_compare, float_round, float_repr


def time_to_float(t):
    return float_round(t.hour + t.minute / 60 + t.second / 3600, precision_digits=2)


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    office_hours = fields.Float(string="Office Planned Hours", compute='_compute_get_working_value')
    different_hours = fields.Float(string="Diff Hours")
    late_comers = fields.Char(string="Late Arrival")
    early_go = fields.Char(string="Early Go")

    @api.depends('employee_id', 'check_in', 'check_out', 'worked_hours')
    @api.onchange('employee_id', 'check_out', 'check_in', 'late_comers', 'early_go')
    def _compute_get_working_value(self):
        for rec in self:
            if rec.employee_id and rec.office_hours == 0:
                for record in rec.employee_id.resource_calendar_id:
                    for attendance in record.attendance_ids:
                        convert_selection = dict(attendance._fields['dayofweek'].selection).get(
                            attendance.dayofweek)
                        attendance_selection = rec.check_in.strftime('%A')
                        if convert_selection == attendance_selection:
                            rec.office_hours = attendance.worked_hours
                            if rec.office_hours >= rec.worked_hours:
                                rec.different_hours = rec.office_hours - rec.worked_hours
                            else:
                                rec.different_hours == '00:00'
                    for attendance_time in record.attendance_ids:
                        convert_selection = dict(attendance_time._fields['dayofweek'].selection).get(
                            attendance_time.dayofweek)
                        attendance_selection = rec.check_in.strftime('%A')
                        if attendance_selection == convert_selection and rec.check_in:
                            check_in = rec.check_in + timedelta(hours=5, minutes=30)
                            convert_check_in = check_in.strftime('%H:%M')
                            float_field_time = timedelta(seconds=attendance_time.hour_from * 60 * 60)
                            dt = datetime.strptime(str(float_field_time), "%H:%M:%S")
                            emp_work_time = dt.time().strftime('%H:%M')
                            worktime = dt.time()
                            checktime = check_in.time()
                            if convert_check_in > emp_work_time:
                                sample = timedelta(hours=checktime.hour, minutes=checktime.minute) - timedelta(
                                    hours=worktime.hour, minutes=worktime.minute)
                                sample1 = datetime.strptime(str(sample), "%H:%M:%S")
                                sample3 = sample1.time().strftime('%H:%M')
                                rec.late_comers = sample3
                            else:
                                rec.late_comers = '00:00'
                        if attendance_selection == convert_selection and rec.check_out:
                            check_out = rec.check_out + timedelta(hours=5, minutes=30)
                            convert_check_out = check_out.strftime('%H:%M')
                            float_hours_to = timedelta(seconds=attendance_time.hour_to * 60 * 60)
                            dt = datetime.strptime(str(float_hours_to), "%H:%M:%S")
                            emp_work_hours_to = dt.time().strftime('%H:%M')
                            worktime_checkout = dt.time()
                            checktime_checkout = check_out.time()
                            if convert_check_out < emp_work_hours_to:
                                samples = timedelta(hours=worktime_checkout.hour,
                                                    minutes=worktime_checkout.minute) - timedelta(
                                    hours=checktime_checkout.hour, minutes=checktime_checkout.minute)
                                samples1 = datetime.strptime(str(samples), "%H:%M:%S")
                                samples3 = samples1.time().strftime('%H:%M')
                                rec.early_go = samples3
                            else:
                                rec.early_go = '00:00'


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    worked_hours = fields.Float(string=" Total Work Hours", compute='_compute_work_hours')

    @api.depends('hour_from', 'hour_to')
    @api.onchange('hour_from', 'hour_to', 'worked_hours')
    def _compute_work_hours(self):
        for rec in self:
            rec.worked_hours = abs(rec.hour_from - rec.hour_to)
