# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class EmployeeEducation(models.Model):
    _name = "employee.education"
    _description = "Employee Education"

    applicant_id = fields.Many2one("hr.applicant", "applicant")
    employee_id = fields.Many2one("hr.employee", "Employee")
    type_id = fields.Many2one("hr.recruitment.degree", "Degree", ondelete="cascade")
    institute_id = fields.Many2one("hr.institute", "Institutes", ondelete="cascade")
    score = fields.Char()
    qualified_year = fields.Date()
    doc = fields.Binary("Transcripts")


class HrInstitute(models.Model):
    _name = "hr.institute"
    _description = "Hr Institute"

    name = fields.Char()
    country_id = fields.Many2one("res.country", "Country")
    state_id = fields.Many2one("res.country.state", "State")


class EmployeeCertification(models.Model):
    _name = "employee.certification"
    _description = "Employee Certification"

    applicant_id = fields.Many2one("hr.applicant", "applicant")
    employee_id = fields.Many2one("hr.employee", "Employee")
    course_id = fields.Many2one("cert.cert", "Course Name", ondelete="cascade")
    levels = fields.Char("Bands/Levels of Completion")
    year = fields.Date("Year of completion")
    doc = fields.Binary("Certificates")


class CertCert(models.Model):
    _name = "cert.cert"
    _description = "Cert Cert"

    name = fields.Char("Course Name")


class EmployeeProfession(models.Model):
    _name = "employee.profession"
    _description = "Employee Profession"

    applicant_id = fields.Many2one("hr.applicant", "applicant")
    employee_id = fields.Many2one("hr.employee", "Employee")
    job_id = fields.Many2one("hr.job", "Job Title")
    location = fields.Char()
    from_date = fields.Date("Start Date")
    to_date = fields.Date("End Date")
    doc = fields.Binary("Experience Certificates")

    _sql_constraints = [
        (
            "to_date_greater",
            "check(to_date > from_date)",
            "Start Date of Professional Experience should be less than End Date!",
        ),
    ]

    @api.constrains("from_date", "to_date")
    def check_from_date(self):
        """
        This method is called when future Start date is entered.
        --------------------------------------------------------
        @param self : object pointer
        """
        today = date.today()
        if (self.from_date > today) or (self.to_date > today):
            raise ValidationError(
                "Future Start Date or End Date in Professional experience is not acceptable!!"
            )
