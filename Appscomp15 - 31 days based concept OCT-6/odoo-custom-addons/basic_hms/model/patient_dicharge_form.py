from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from io import BytesIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from random import choice
from string import digits
from pygame import mixer


class PatientDischarge(models.Model):
    _name = 'patient.discharge'
    _description = ' Patient Discharge Form'

    partner_id = fields.Many2one('res.partner', string="Patient Name", required=True)
    admitted_date = fields.Datetime(string='Admitted Date')
    reason_admittance = fields.Text(string="Reason for Admittance")
    diagnosis_admittance = fields.Text(string="Diagnosis At Admittance")
    treatment_summary = fields.Text(string="Treatment Summary")
    date_discharged = fields.Datetime(string='Date Discharged')
    diagnosis_discharge = fields.Text(string="Diagnosis At Discharge")
    further_treatment_plan = fields.Text(string="Further Treatment Plan")
    next_checkup_date = fields.Datetime(string='Next Checkup Date')
    notes = fields.Text(string="Notes")
    physician_approved = fields.Selection([('0', 'Yes'), ('1', 'No')], 'Physician approved ?')
    reason_discharge = fields.Selection([('0', 'Patient deceased'), ('1', 'Patient terminated without')],
                                        'Reason for discharge')
    client_consent = fields.Selection([('0', 'Yes'), ('1', 'No')], 'Client consent/Approval?')
    patient_discharge_line_ids = fields.One2many('patient.discharge.line', 'name', 'Medication Prescribed')


class PatientDischargeLine(models.Model):
    _name = "patient.discharge.line"
    _description = 'medical Discharge line'

    name = fields.Many2one('patient.discharge', 'Patient Discharge')
    product_id = fields.Many2one('product.product', 'Medication')
    dosage_quantity = fields.Integer('Dosage')
    amount = fields.Float('Amount')
    frequency = fields.Char('Frequency')
    end_date = fields.Datetime('End Date')
