from odoo import models, api, _, fields
from twilio.rest import Client

class birthday_sms_cron_action(models.Model):
    _name = 'birthday.sms'

    def birthday_sms(self):
        today = fields.Date.today()
        api_data = self.env['api.configure'].search([])
        template_data = self.env['birthday.template'].search([])
        emp_data = self.env['res.partner'].search([])
        for emp in emp_data:
            if emp.date_of_birth:
                if emp.date_of_birth == today:
                    for acc in api_data:
                        client = Client(acc.sid, acc.auth_key)
                        for template in template_data:
                            client.messages.create(body=template.birthday_sms_content, to=emp.mobile, from_=acc.from_no)