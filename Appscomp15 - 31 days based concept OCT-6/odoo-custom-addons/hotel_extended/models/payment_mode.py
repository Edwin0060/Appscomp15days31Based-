from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PaymentMode(models.Model):
    _name = 'payment.mode'
    _description = 'Payment Mode Register'

    name = fields.Char(string='Payment Mode')
    payment_mode_img = fields.Binary(string='Payment Logo')

    @api.constrains('name')
    def _check_identity_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                code = self.sudo().search(domain)
                if len(code) > 1:
                    for i in range(len(code)):
                        if code[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  The Payment Mode  of - %s is already exists.\n'
                                  'Please check it.....') % (
                                    record.name))
