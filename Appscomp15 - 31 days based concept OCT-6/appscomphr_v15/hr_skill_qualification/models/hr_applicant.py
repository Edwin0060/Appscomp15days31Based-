# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software PVT. LTD.
# See LICENSE file for full copyright & licensing details.

from odoo import fields, models


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    techskill_ids = fields.One2many(
        "emp.tech.skills", "applicant_id", "Technical Skills"
    )
    nontechskill_ids = fields.One2many(
        "emp.nontech.skills", "applicant_id", "Non-Technical Skills"
    )
    education_ids = fields.One2many("employee.education", "applicant_id", "Education")
    certification_ids = fields.One2many(
        "employee.certification", "applicant_id", "Certification"
    )
    profession_ids = fields.One2many(
        "employee.profession", "applicant_id", "Professional Experience"
    )

    def create_employee_from_applicant(self):
        """Create an hr.employee from the hr.applicants"""
        res = super(HrApplicant, self).create_employee_from_applicant()
        for applicant in self:
            res["context"].update(
                {
                    "default_techskill_ids": [(6, 0, applicant.techskill_ids.ids)],
                    "default_nontechskill_ids": [
                        (6, 0, applicant.nontechskill_ids.ids)
                    ],
                    "default_education_ids": [(6, 0, applicant.education_ids.ids)],
                    "default_certification_ids": [
                        (6, 0, applicant.certification_ids.ids)
                    ],
                    "default_profession_ids": [(6, 0, applicant.profession_ids.ids)],
                }
            )
        return res
