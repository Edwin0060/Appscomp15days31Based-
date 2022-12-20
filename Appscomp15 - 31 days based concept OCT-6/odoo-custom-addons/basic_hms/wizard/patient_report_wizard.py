from odoo import api, fields, models, _
from datetime import datetime


class PatientFitnessCertificateReport(models.TransientModel):
    _name = "patient.fitness.certificate.report"
    _description = 'Patient Fitness Certificate Report'

    name = fields.Char(string="Patient Name")
    patient_age = fields.Char(string="Patient Age")
    patient_gender = fields.Char(string="Patient Gender")
    patient_image = fields.Binary(string='')
    fitness_remark1 = fields.Text(default='THIS IS TO CERTIFY THAT MRS.')
    fitness_remark2 = fields.Text(default='Selected "Patient" Name')
    fitness_remark3 = fields.Text(default=', AGED')
    fitness_remark4 = fields.Text(default='Selected "Patient" Age')
    fitness_remark5 = fields.Text(default='Selected "Patient" Gender')
    fitness_remark6 = fields.Text(default='.DIAGNOSED AS MICRO LUMBAR DISCECTOMY.THE PATIENT CONSULTS OUR DOCTOR AS '
                                          'PER CHECKUP PATIENT NEEDS SURGERY. SO PATIENTS SON WANT TO TAKE CARE OF '
                                          'MOTHER. SO HER SON WANTS TO TAKE LEAVE AND GIVE HIM A PERMISSION FOR HIS '
                                          'MOTHERS SURGERY.')
    final_remark = fields.Text(string='Final OutCome')
    doctor = fields.Char(string="Primary Care Doctor")
    place = fields.Char(string="Place")

    @api.onchange('fitness_remark1', 'fitness_remark2', 'fitness_remark3', 'fitness_remark4', 'fitness_remark5',
                  'fitness_remark6', 'patient_age', 'patient_gender', 'name')
    def onchange_final_outcome(self):
        for rec in self:
            if rec.fitness_remark1 and rec.name and rec.fitness_remark3  \
                    and rec.fitness_remark6:
                rec.final_remark = rec.fitness_remark1 + rec.name.upper() + ' ' + rec.fitness_remark3 + ' ' \
                                   + rec.patient_age + ' ' + rec.patient_gender.upper() + ' ' + rec.fitness_remark6

    def patient_fitness_report_print(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'patient_name': self.name,
                'patient_age': self.patient_age,
                'patient_gender': self.patient_gender,
                'patient_image': self.patient_image,
                'final_remark': self.final_remark,
                'patient_doctor': self.doctor,
                'patient_place': self.place.upper(),

            },
        }
        return self.env.ref('basic_hms.report_fitness_report_action').report_action(self, data=data, )



class ReportActionRender(models.AbstractModel):
    _name = 'report.basic_hms.report_fitness_report_qweb_report'
    _description = 'Fitness Report Render'

    def _get_report_values(self, docids, data=None):
        patient_name = data['form']['patient_name']
        patient_age = data['form']['patient_age']
        patient_gender = data['form']['patient_gender']
        patient_image = data['form']['patient_image']
        final_remark = data['form']['final_remark']
        patient_doctor = data['form']['patient_doctor']
        patient_place = data['form']['patient_place']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'patient_name': patient_name,
            'patient_age': patient_age,
            'patient_gender': patient_gender,
            'patient_image': patient_image,
            'final_remark': final_remark,
            'patient_doctor': patient_doctor,
            'patient_place': patient_place,

        }
