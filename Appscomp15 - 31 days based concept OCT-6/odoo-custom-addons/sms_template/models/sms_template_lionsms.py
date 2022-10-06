# -*- coding: utf-8 -*-
from odoo import http, models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    def get_employee_login_alert(self):
        import requests
        print("************************************************")
        url = "https://msg.lionsms.com/api/smsapi?key=521df5d0cafd14ee8afc8f32f7431500&" \
              "route=1&sender=APPSCM&number=%s&sms=Dear RBS," \
              " Greetings form AppsComp.This is your time of check in 9.30 " \
              "am&templateid=1707166132146005049" % (
                  self.mobile_phone)
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", url)
        payload = {}
        headers = {
            'Cookie': 'ci_session=i67moorl7ljmdud54nk5bf808tdkdsi1'
        }
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
        print(response.text)
