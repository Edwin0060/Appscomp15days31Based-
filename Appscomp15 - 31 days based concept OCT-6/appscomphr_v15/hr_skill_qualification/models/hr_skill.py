# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import fields, models, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    techskill_ids = fields.One2many(
        "emp.tech.skills", "employee_id", "Technical Skills"
    )
    nontechskill_ids = fields.One2many(
        "emp.nontech.skills", "employee_id", "Non-Technical Skills"
    )
    education_ids = fields.One2many("employee.education", "employee_id", "Education")
    certification_ids = fields.One2many(
        "employee.certification", "employee_id", "Certification"
    )
    profession_ids = fields.One2many(
        "employee.profession", "employee_id", "Professional Experience"
    )


class EmployeeTechSkills(models.Model):
    _name = "emp.tech.skills"
    _description = "Employee Tech Skills"

    applicant_id = fields.Many2one("hr.applicant", "applicant")
    employee_id = fields.Many2one("hr.employee", "Employee")
    tech_id = fields.Many2one("tech.tech", "Technical Skills", ondelete="cascade")
    levels = fields.Selection(
        [("basic", "Basic"), ("medium", "Medium"), ("advance", "Advance")], "Levels"
    )


class TechTech(models.Model):
    _name = "tech.tech"
    _description = "Tech Tech"

    name = fields.Char()

    def unlink(self):
        """
        This method is called user tries to delete a skill which
        is already in use by an employee.
        --------------------------------------------------------
        @param self : object pointer
        """
        tech_skill = self.env["emp.tech.skills"].search([("tech_id", "in", self.ids)])
        print(tech_skill)
        if tech_skill:
            raise UserError(
                _(
                    "You are trying to delete a Skill which is referenced by an Employee."
                )
            )
        return super(TechTech, self).unlink()


class EmployeeNonTechSkills(models.Model):
    _name = "emp.nontech.skills"
    _description = "Employee Non Tech Skills"

    applicant_id = fields.Many2one("hr.applicant", "Applicant")
    employee_id = fields.Many2one("hr.employee", "Employee")
    nontech_id = fields.Many2one(
        "nontech.nontech", "Non-Technical Skills", ondelete="cascade"
    )
    levels = fields.Selection(
        [("basic", "Basic"), ("medium", "Medium"), ("advance", "Advance")], "Levels"
    )


class NontechNontech(models.Model):
    _name = "nontech.nontech"
    _description = "Nontech Nontech"

    name = fields.Char()

    def unlink(self):
        """
        This method is called user tries to delete a skill which
        is already in use by an employee.
        --------------------------------------------------------
        @param self : object pointer
        """
        tech_skill = self.env["emp.nontech.skills"].search(
            [("nontech_id", "in", self.ids)]
        )
        if tech_skill:
            raise UserError(
                _(
                    "You are trying to delete a Skill which is referenced by an Employee."
                )
            )
        return super(NontechNontech, self).unlink()
