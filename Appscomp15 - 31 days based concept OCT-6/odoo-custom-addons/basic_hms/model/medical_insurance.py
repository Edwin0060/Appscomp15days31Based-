# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class medical_insurance(models.Model):
    _name = 'medical.insurance'
    _description = 'medical insurance'
    _rec_name = 'insurance_compnay_id'

    number = fields.Char('Number')
    medical_insurance_partner_id = fields.Many2one('res.partner','Owner',required=True)
    patient_id = fields.Many2one('res.partner', 'Owner')
    type = fields.Selection([('start_health', 'Star Health'), ('chch_istn', 'CMCH ISTN'),
                             ('gmps', 'Government Employee & pensioner Scheme'),
                             ('hdfc', 'HDFC'), ('cholamandalam', 'Chola Mandalam'), ('ifkco_tokyo', 'IFKCO TOKYO')],
                            'Insurance Type')
    member_since = fields.Date('Member Since')
    insurance_compnay_id = fields.Many2one('res.partner', domain=[('is_insurance_company', '=', True)],
                                           string='Insurance Company')
    category = fields.Char('Category')
    notes= fields.Text('Extra Info')
    member_exp = fields.Date('Expiration Date')
    medical_insurance_plan_id = fields.Many2one('medical.insurance.plan','Plan')

    attachment = fields.Many2many('ir.attachment', string="Multi Attachments")
    attachment_name = fields.Char(string="Multi Attachment")

    pre_authority_form = fields.Boolean(string='Pre Authority Form')
    pre_authority_form_attachment = fields.Binary(string="Attachments")
    pre_authority_form_attachment_name = fields.Char(string="Attachment")

    lab_report = fields.Boolean(string='X-Ray, MRI, CT, Blood Report')
    lab_report_attachment = fields.Binary(string="Attachments")
    lab_report_attachment_name = fields.Char(string="Attachment")

    patient_photo = fields.Boolean(string='Patient Photo')
    patient_photo_attachment = fields.Binary(string="Attachments")
    patient_photo_attachment_name = fields.Char(string="Attachment")

    insurance_id = fields.Boolean(string='Insurance ID')
    insurance_id_attachment = fields.Binary(string="Attachments")
    insurance_id_attachment_name = fields.Char(string="Attachment")

    discharge_Summary = fields.Boolean(string='Discharge Summary')
    discharge_Summary_attachment = fields.Binary(string="Attachments")
    discharge_Summary_attachment_name = fields.Char(string="Attachment")

    final_bill = fields.Boolean(string='Final Bill')
    final_bill_attachment = fields.Binary(string="Attachments")
    final_bill_attachment_name = fields.Char(string="Attachment")

    post_xray = fields.Boolean(string='Post XRay')
    post_xray_attachment = fields.Binary(string="Attachments")
    post_xray_attachment_name = fields.Char(string="Attachment")

    post_clinical_picture = fields.Boolean(string='Post Clinical Picture')
    post_clinical_picture_attachment = fields.Binary(string="Attachments")
    post_clinical_picture_attachment_name = fields.Char(string="Attachment")

    lab_bills = fields.Boolean(string='Lab Bills')
    lab_bills_attachment = fields.Binary(string="Attachments")
    lab_bills_attachment_name = fields.Char(string="Attachment")

    medical_bill = fields.Boolean(string='Medical Bill')
    medical_bill_attachment = fields.Binary(string="Attachments")
    medical_bill_attachment_name = fields.Char(string="Attachment")

    progress_notes = fields.Boolean(string='Progress Note')
    progress_notes_attachment = fields.Binary(string="Attachments")
    progress_notes_attachment_name = fields.Char(string="Attachment")

    operation_records = fields.Boolean(string='Operation Record')
    operation_records_attachment = fields.Binary(string="Attachments")
    operation_records_attachment_name = fields.Char(string="Attachment")

    implant_sticker = fields.Boolean(string='Implant Sticker')
    implant_sticker_attachment = fields.Binary(string="Attachments")
    implant_sticker_attachment_name = fields.Char(string="Attachment")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
