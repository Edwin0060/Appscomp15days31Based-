# -*- coding: utf-8 -*-

from odoo import models, fields, api


class education_history(models.Model):
    _inherit = 'hr.employee'
    _description = 'education_history.education_history'

    relation = fields.One2many('education.education','rlfield')
    attachment = fields.Many2many('ir.attachment', String="Attachments")

class education_history(models.Model):
    _name = 'degree.degree'
    _description = 'Degree.Name'

    name = fields.Char(string='Degree')

class education_institute(models.Model):
    _name = 'institute.institute'
    _description = 'institute.institute'

    name = fields.Char(string='Institute')


class education_history(models.Model):
    _name = 'level.level'
    _description = 'Level.level'

    name = fields.Char(string='Level')

class education_department(models.Model):
    _name = 'department.department'
    _description = 'Department'

    name = fields.Char(string='Department')


class employee_history(models.Model):
    _name = 'education.education'
    _description = 'Department'
    detail = fields.Char(string='Details')

    rlfield=fields.Many2one("hr.employee")
    department = fields.Many2one("department.department", string='Department')
    degree = fields.Many2one("degree.degree", string='Degree')
    institute = fields.Many2one("institute.institute", string='Institute')
    level = fields.Char(string='Level')
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')