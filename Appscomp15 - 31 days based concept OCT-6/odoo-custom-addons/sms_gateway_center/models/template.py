from odoo import models, api, _, fields

class template_sms(models.Model):
    _name = 'template.sms'
    _description = 'SMS Templates'

    name = fields.Char(string='Template Name', required=False)
    sms_content = fields.Text(string='Sms Content', required=False)

class mult_sms_group(models.Model):
    _name = 'multiple.sms.group'
    _description = 'Multiple SMS Group'

    name = fields.Char(string='Group Name', required=True)
    add_people = fields.Many2many(comodel_name='res.partner', required=True)

class birthday_template(models.Model):
    _name = 'birthday.template'
    _description = 'Birthday Template'

    birthday_sms_content = fields.Text(string='Birthday SMS Content', required=True)