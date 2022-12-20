import time

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta



class MedicalPatient(models.Model):
    _inherit = 'medical.patient'
    _description = 'Medical Patient'

    time = fields.Selection([
        ('1', '1 hour'),
        ('2', '2 hour'),
        ('3', '3 hour'),
    ], default='1')
    waiting_time = fields.Selection([('1', 'One'), ('2', 'Two'), ('3', 'Three')], string='Waiting',
                                    default='1')

    def get_patient_values(self):
        today = date.today()
        patient_data_list = []
        patient_data = self.env['medical.patient'].sudo().search([('create_date', '>=', today),
                                                                  ('state', '=', 'register')])
        for i in patient_data:
            patient_data_list.append({
                'id': i.id,
                'name': i.name,
                'patient_id': i.patient_name,
                'patient_category': i.patient_category,
                # 'patient_type': i.patient_type,
                'mobile_number': i.mobile_number,
                'patient_email': i.patient_email,
                'sex': dict(i._fields['sex'].selection).get(i.sex),
                'marital_status': dict(i._fields['marital_status'].selection).get(i.marital_status),
                'age': i.age,
                'primary_care_physician_id': i.primary_care_physician_id.partner_id.name,
                'primary_care_physician_code': i.primary_care_physician_id.code,
                'state': i.state,
                'time': i.waiting_time,
                'token': i.token_number,
            })

        return patient_data_list

    def cron_patient_state_alert(self):
        partner_id = self.env['medical.patient'].search([])
        for patient in partner_id:
            crn_datetime = datetime.now()
            wait_time = crn_datetime - patient.create_date
            check = str(wait_time).split(':')[1]
            if patient.create_date.date() == crn_datetime.date() and patient.state == 'register':
                if check == '12':
                    patient.write({
                        'waiting_time': '2',
                    })
                elif check == '03':
                    patient.write({
                        'waiting_time': '3',
                    })
