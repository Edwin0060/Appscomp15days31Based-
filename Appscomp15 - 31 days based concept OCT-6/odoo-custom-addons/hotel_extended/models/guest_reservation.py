from odoo import fields, models, api, _, exceptions
from datetime import datetime
from odoo.exceptions import ValidationError


class Keys(models.Model):
    _name = 'customer.register'
    _description = 'Guest Register'

    name = fields.Char(string='Guest Name')
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string='E-mail')
    valid_proof = fields.Many2one("identity.register", "Proof Type")
    identity_img = fields.Binary(string='Identity upload')
    proof_attch = fields.Char(string='Attachment')
    proof_num = fields.Char(string='Proof Number')

    street = fields.Char(string='Street', readonly=False, store=True)
    street2 = fields.Char('Street2', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, readonly=False, store=True)
    city = fields.Char('City', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State', readonly=False, store=True, )
    country_id = fields.Many2one(
        'res.country', string='Country', readonly=False, store=True)

    description = fields.Html('Notes')
    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High')],
        string='Priority')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('checked_in', 'Checked-In'),
        ('checked_out', 'Checked-Out'),
        ('payment', 'Payment Done'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')],
        default='draft')
    user_guest_count = fields.Integer(string="Reservation", compute='get_use_count')


    def get_use_count(self):
        self.user_guest_count = self.env['hotel.reservation'].sudo().search_count([
            ('partner_id.name', '=', self.name)])

    def get_guest_list(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('hotel_extended.view_hotel_reservation_form')
        tree_view = self.sudo().env.ref('hotel_extended.view_hotel_reservation_tree')
        return {
            'name': _('My Reservation'),
            'res_model': 'hotel.reservation',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('partner_id.name', '=', self.name)],
        }
    def create_res_partner_and_reservation(self):
        for val in self:
            values = {
                'name': val.name,
            }
            self.env['res.partner'].create(values)
            partner = self.env['res.partner'].search([
                ('name', '=', self.name)])
            values_2 = {
                'partner_id': partner.id,
                'pricelist_id': 1,
                'checkin': datetime.today(),
                'checkout': datetime.today(),
            }
            self.env['hotel.reservation'].create(values_2)
        self.write({
            'state': 'booked',
        })


class Identity(models.Model):
    _name = 'identity.register'
    _description = 'Identity Register'

    name = fields.Char(string='Identity Name')

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
                                _('Alert !!  The Identity Type of - %s is already exists.\n'
                                  'Please check it.....') % (
                                    record.name))


