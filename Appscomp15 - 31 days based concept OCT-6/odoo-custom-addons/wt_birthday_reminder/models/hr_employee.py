# -*- coding: utf-8 -*-

from odoo import models
from datetime import date


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def birthday_reminder(self):
        month = date.today().month
        day = date.today().day
        for employee in self.search([('birthday', '!=', False)]):
            if employee.birthday.day == day and employee.birthday.month == month:
                self.env.ref('wt_birthday_reminder.mail_template_birthday_wish').send_mail(employee.id, force_send=True)
                all_email = self.search([('id', '!=', employee.id)]).mapped('work_email')
                email_values = {'email_to': ','.join(all_email)}
                self.env.ref('wt_birthday_reminder.mail_template_birthday_reminder').send_mail(employee.id, email_values=email_values, force_send=True)
