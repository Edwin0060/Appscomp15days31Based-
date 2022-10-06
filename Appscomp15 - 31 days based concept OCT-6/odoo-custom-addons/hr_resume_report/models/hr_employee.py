# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    barcode = fields.Char(
        'Employee Id (badge)', help="ID Used for Employee Identification")
