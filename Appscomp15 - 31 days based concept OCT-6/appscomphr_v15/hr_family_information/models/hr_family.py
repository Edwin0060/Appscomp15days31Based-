from odoo import models, fields, api
from odoo.addons.phone_validation.tools import phone_validation


GENDER_SELECTION = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
]
CERTIFICATE_SELECTION = [
    ('elementary School', 'Elementary School'),
    ('junior high school', 'Junior High School'),
    ('graduate', 'Senior High School'),
    ('bachelor', 'Bachelor'),
    ('master', 'Master'),
    ('doctor', 'Doctor'),
    ('other', 'Other'),
]


class HrFamilyInfo(models.Model):
    _name = 'hr.family.info'
    _description = 'Employee Family Information'

    identification_id = fields.Char('Identification Id')
    name = fields.Char('Name', required='1')
    gender = fields.Selection(GENDER_SELECTION, 'gender')
    birthday = fields.Date('Date Of Birth')
    relation_id = fields.Many2one('hr.employee.relation', 'Relation')
    mobile = fields.Char('Mobile')
    certificate = fields.Selection(CERTIFICATE_SELECTION, 'Certificate Level',
                                   default='other', groups="hr.group_hr_user")
    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee',
                                  invisible=1)
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', related='employee_id.country_id')

    @api.onchange('mobile', 'country_id')
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = self._phone_format(self.mobile)

    def _phone_format(self, number, country=None, company=None):
        country = country or self.country_id or self.env.company.country_id
        if not country:
            return number
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            force_format='INTERNATIONAL',
            raise_exception=False
        )


class HrEmployeeRelation(models.Model):
    _name = 'hr.employee.relation'
    _description = 'Relation'

    name = fields.Char('Name')
    abbreviation = fields.Char('Abbreviation')


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    spouse_identification_id = fields.Char('Identification Id')
    family_ids = fields.One2many(
        'hr.family.info', 'employee_id', string='Family', help='Family Information')

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    spouse_identification_id = fields.Char('Identification Id')
    family_ids = fields.One2many(
        'hr.family.info', 'employee_id', string='Family', help='Family Information')