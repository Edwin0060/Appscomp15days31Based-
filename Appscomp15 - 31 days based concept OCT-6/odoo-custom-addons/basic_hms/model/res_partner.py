# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class res_partner(models.Model):
    _inherit = 'res.partner'

    relationship = fields.Char(string='Relationship')
    relative_partner_id = fields.Many2one('res.partner',string="Relative_id")
    is_patient = fields.Boolean(string='Patient')
    is_person = fields.Boolean(string="Person")
    is_doctor = fields.Boolean(string="Doctor")
    is_insurance_company = fields.Boolean(string='Insurance Company')
    is_pharmacy = fields.Boolean(string="Pharmacy")
    patient_insurance_ids = fields.One2many('medical.insurance','patient_id')
    is_institution = fields.Boolean('Institution')
    company_insurance_ids = fields.One2many('medical.insurance','insurance_compnay_id','Insurance')
    reference = fields.Char('ID Number')

    @api.constrains('mobile')
    def _check_name(self):
        for record in self:
            if record.name:
                domain = [('mobile', '=', record.mobile)]
                name = self.search(domain)
                if len(name) > 1:
                    for i in range(len(name)):
                        if name[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  The Employee Mobile Number of - %s already exists.') % (
                                    record.mobile))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: