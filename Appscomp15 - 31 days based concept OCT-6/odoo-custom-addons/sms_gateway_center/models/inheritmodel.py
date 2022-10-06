from odoo import models, api, _, fields

class BirthdayField(models.Model):
    _inherit = 'res.partner'
    date_of_birth = fields.Date(string="Date of Birth")