# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Jesni Banu and Nilmar Shereef(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class LaundryManagement(models.Model):
    _name = 'laundry.order'
    _inherit = 'mail.thread'
    _description = "Laundry Order"
    _order = 'order_date desc, id desc'


    @api.depends('order_lines')
    def get_total(self):
        total = 0
        for obj in self:
            for each in obj.order_lines:
                total += each.amount
            obj.total_amount = total

    def confirm_order(self):
        self.state = 'order'
        sale_obj = self.env['sale.order'].create(
            {'partner_id': self.partner_id.id,
             'partner_invoice_id': self.partner_invoice_id.id,
             'partner_shipping_id': self.partner_shipping_id.id})
        self.sale_obj = sale_obj
        product_id = self.env.ref('laundry_management.laundry_service')
        self.env['sale.order.line'].create({'product_id': product_id.id,
                                            'name': 'Laundry Service',
                                            'price_unit': self.total_amount,
                                            'order_id': sale_obj.id
                                            })
        for each in self:
            for obj in each.order_lines:
                self.env['washing.washing'].create(
                    {'name': obj.product_id.name + '-Washing',
                     'user_id': obj.washing_type.assigned_person.id,
                     'description': obj.description,
                     'laundry_obj': obj.id,
                     'state': 'draft',
                     'washing_date': datetime.now().strftime(
                         '%Y-%m-%d %H:%M:%S')})

    def create_invoice(self):
        if self.sale_obj.state in ['draft', 'sent']:
            self.sale_obj.action_confirm()
        self.invoice_status = self.sale_obj.invoice_status
        return {
            'name': 'Create Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.advance.payment.inv',
            'type': 'ir.actions.act_window',
            'context': {'laundry_sale_obj': self.sale_obj.id},
            'target': 'new'
        }

    def return_dress(self):
        self.state = 'return'

    def cancel_order(self):
        self.state = 'cancel'

    def set_as_draft(self):
        self.state = 'draft'

    def _invoice_count(self):
        wrk_ordr_ids = self.env['account.move'].search([('invoice_origin', '=', self.sale_obj.name)])
        self.invoice_count = len(wrk_ordr_ids)

    def _work_count(self):
        if self.id:
            wrk_ordr_ids = self.env['washing.washing'].search([('laundry_obj.laundry_obj.id', '=', self.id)])
            self.work_count = len(wrk_ordr_ids)
        else:
            self.work_count = False

    def action_view_laundry_works(self):

        work_obj = self.env['washing.washing'].search(
            [('laundry_obj.laundry_obj.id', '=', self.id)])
        work_ids = []
        for each in work_obj:
            work_ids.append(each.id)
        view_id = self.env.ref('laundry_management.washing_form_view').id
        if work_ids:
            if len(work_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'washing.washing',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Works'),
                    'res_id': work_ids and work_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', work_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'washing.washing',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Works'),
                    # 'res_id': work_ids
                }
            return value

    def action_view_invoice(self):

        inv_obj = self.env['account.move'].search(
            [('invoice_origin', '=', self.sale_obj.name)])
        inv_ids = []
        for each in inv_obj:
            inv_ids.append(each.id)
        view_id = self.env.ref('account.view_move_form').id
        if inv_ids:
            if len(inv_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'res_id': inv_ids and inv_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', inv_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'res_id': inv_ids
                }

            return value





    name = fields.Char(string="Label", default="/", readonly=True)
    # proforma_id = fields.Many2one('hotel.folio', string="Proforma")
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', invisible=1, related='sale_obj.invoice_status',
        store=True)
    sale_obj = fields.Many2one('sale.order', invisible=1)
    invoice_count = fields.Integer(compute='_invoice_count',
                                   string='# Invoice')
    work_count = fields.Integer(compute='_work_count', string='# Works')
    partner_id = fields.Many2one('res.partner', string='Guest',
                                 readonly=True,
                                 states={'draft': [('readonly', False)],
                                         'order': [('readonly', False)]},
                                 required=True,
                                 change_default=True, index=True,
                                 track_visibility='always')
    partner_invoice_id = fields.Many2one('res.partner',
                                         string='Invoice Address',
                                         readonly=True, required=True,
                                         states={
                                             'draft': [('readonly', False)],
                                             'order': [('readonly', False)]},
                                         help="Invoice address for current sales order.")
    partner_shipping_id = fields.Many2one('res.partner',
                                          string='Delivery Address',
                                          readonly=True, required=True,
                                          states={
                                              'draft': [('readonly', False)],
                                              'order': [('readonly', False)]},
                                          help="Delivery address for current sales order.")
    order_date = fields.Datetime(string="Date",
                                 default=datetime.now().strftime(
                                     '%Y-%m-%d %H:%M:%S'))
    laundry_person = fields.Many2one('res.users', string='Laundry Person',
                                     required=1)
    order_lines = fields.One2many('laundry.order.line', 'laundry_obj',
                                  required=1, ondelete='cascade')
    total_amount = fields.Float(compute='get_total', string='Total', store=1)
    currency_id = fields.Many2one("res.currency", string="Currency")
    note = fields.Text(string='Terms and conditions')
    inter_laundry = fields.Boolean(
        "Is Internal or External??", help="is guest reside in hotel or not"
    )
    laundry_activity_type = fields.Selection(
        [
            ("internal", "Internal laundry "),
            ("external", " External laundry"),
        ],
        "Activity Type", default=False)

    hotel_laundary_room_id = fields.Many2one("hotel.room", "Room")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('order', 'Laundry Order'),
        ('process', 'Processing'),
        ('done', 'Done'),
        ('return', 'Returned'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True,
        track_visibility='onchange', default='draft')

    landry_cancel_remarks = fields.Text(string='Landry Cancel Remarks')
    landry_cancel_remarks_2 = fields.Text(string='Landry Cancel Remarks')
    res_id = fields.Many2one("hotel.reservation", "Ref No")
    floor_no = fields.Many2one("hotel.floor", "Floor No")
    categ = fields.Many2one("hotel.room.type", "Room")
    room_number = fields.Char("Room No")
    room_num_in_squ = fields.Char("Number")

    @api.onchange('room_number','floor_no','categ')
    def onchange_room_number(self):
        floor = self.floor_no.short_code
        category = self.categ.short_code
        if floor and category and self.room_number:
            self.room_num_in_squ = str(floor) + '/' + str(category) + '/' + str(self.room_number)



    @api.onchange('res_id')
    def fetch_details(self):
        self.partner_id = self.res_id.partner_id
        self.partner_invoice_id = self.res_id.partner_invoice_id
        self.partner_shipping_id = self.res_id.partner_order_id

    def hotel_landry_cancel(self):
        view_id = self.env['landry.order.cancel']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hotel Management Laundry Order Cancel Remarks',
            'res_model': 'landry.order.cancel',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('laundry_management.hotel_management_landry_cancel_remarks_wizard', False).id,
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            if vals.get('laundry_activity_type') == 'internal':
                vals['name'] = self.env['ir.sequence'].next_by_code('laundry.internal.order') or '/'
            if vals.get('laundry_activity_type') == 'external':
                vals['name'] = self.env['ir.sequence'].next_by_code('laundry.external.order') or '/'

        return super(LaundryManagement, self).create(vals)


class LaundryManagementLine(models.Model):
    _name = 'laundry.order.line'

    @api.depends('washing_type', 'extra_work', 'qty')
    def get_amount(self):
        for obj in self:
            total = obj.washing_type.amount * obj.qty
            for each in obj.extra_work:
                total += each.amount * obj.qty
            obj.amount = total

    product_id = fields.Many2one('product.product', string='Dress', required=1)
    qty = fields.Integer(string='No of items', required=1)
    description = fields.Text(string='Description')
    washing_type = fields.Many2one('washing.type', string='Washing Type',
                                   required=1)
    extra_work = fields.Many2one('washing.work', string='Extra Work')
    amount = fields.Float(compute='get_amount', string='Amount')
    laundry_obj = fields.Many2one('laundry.order', invisible=1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('wash', 'Washing'),
        ('extra_work', 'Make Over'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')


class WashingType(models.Model):
    _name = 'washing.type'

    name = fields.Char(string='Name', required=1)
    assigned_person = fields.Many2one('res.users', string='Assigned Person',
                                      required=1)
    amount = fields.Float(string='Service Charge', required=1)

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                code = self.search(domain)
                if len(code) > 1:
                    for i in range(len(code)):
                        if code[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  The Washing Type of - %s is already exists.\n'
                                  'Please check it.....') % (
                                    record.name))


class ExtraWork(models.Model):
    _name = 'washing.work'

    name = fields.Char(string='Name', required=1)
    assigned_person = fields.Many2one('res.users', string='Assigned Person',
                                      required=1)
    amount = fields.Float(string='Service Charge', required=1)

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                code = self.search(domain)
                if len(code) > 1:
                    for i in range(len(code)):
                        if code[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  The Additional Work of - %s is already exists.\n'
                                  'Please check it.....') % (
                                    record.name))


class Washing(models.Model):
    _name = 'washing.washing'
    _description = 'Laundry Work Order'

    def start_wash(self):
        if not self.laundry_works:
            self.laundry_obj.state = 'wash'
            self.laundry_obj.laundry_obj.state = 'process'
        for each in self:
            for obj in each.product_line:
                self.env['sale.order.line'].create(
                    {'product_id': obj.product_id.id,
                     'name': obj.name,
                     'price_unit': obj.price_unit,
                     'order_id': each.laundry_obj.laundry_obj.sale_obj.id,
                     'product_uom_qty': obj.quantity,
                     'product_uom': obj.uom_id.id,
                     })
        self.state = 'process'

    def get_service_order_line_items(self):
        line_vals = []
        for line in self.laundry_obj.laundry_obj.order_lines:
            if line.extra_work:
                rate = line.washing_type.amount + line.extra_work.amount
            else:
                rate = line.washing_type.amount
            if line:
                vals = [0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty,
                    'name': self.name + '/' + line.product_id.name,
                    'price_unit': rate,
                }]
                line_vals.append(vals)
        return line_vals

    def set_to_done(self):
        self.state = 'done'
        f = 0
        if not self.laundry_works:
            if self.laundry_obj.extra_work:
                for each in self.laundry_obj.extra_work:
                    self.create({'name': each.name,
                                 'user_id': each.assigned_person.id,
                                 'description': self.laundry_obj.description,
                                 'laundry_obj': self.laundry_obj.id,
                                 'state': 'draft',
                                 'laundry_works': True,
                                 'washing_date': datetime.now().strftime(
                                     '%Y-%m-%d %H:%M:%S')})
                self.laundry_obj.state = 'extra_work'
        laundry_obj = self.search([('laundry_obj.laundry_obj', '=',
                                    self.laundry_obj.laundry_obj.id)])
        for each in laundry_obj:
            if each.state != 'done' or each.state == 'cancel':
                f = 1
                break
        if f == 0:
            self.laundry_obj.laundry_obj.state = 'done'
            if self.laundry_obj.laundry_obj.res_id:
                folio_id = self.env["hotel.folio"].search([("reservation_id", "=", self.laundry_obj.laundry_obj.res_id.id)])
            else:
                folio_id = self.env["hotel.folio"].search([("room_num_floor", "=", self.laundry_obj.laundry_obj.room_num_in_squ)])

            folio_id.sudo().write({
                'service_line_ids': self.get_service_order_line_items(),
            })
            print("ooooooooooooooooooooooooooooooooo",folio_id)
            if folio_id:
                line_vals = []
                vals = [0, 0, {
                    "name": self.laundry_obj.laundry_obj.name,
                    "partner_id": self.laundry_obj.laundry_obj.partner_id.id,
                    "order_date": self.laundry_obj.laundry_obj.order_date,
                    "laundry_person": self.laundry_obj.laundry_obj.laundry_person.id,
                    "total_amount": self.laundry_obj.laundry_obj.total_amount,
                }]
                line_vals.append(vals)
            else:
                raise ValidationError(_("Alert!, Please Create a Folio against the Reservation"))
            folio_id.update({
                'hotel_laundry_orders': line_vals,
            })
        laundry_obj1 = self.search([('laundry_obj', '=', self.laundry_obj.id)])
        f1 = 0
        for each in laundry_obj1:
            if each.state != 'done' or each.state == 'cancel':
                f1 = 1
                break
        if f1 == 0:
            self.laundry_obj.state = 'done'

    @api.depends('product_line')
    def get_total(self):
        total = 0
        for obj in self:
            for each in obj.product_line:
                total += each.subtotal
            obj.total_amount = total

    name = fields.Char(string='Work')
    laundry_works = fields.Boolean(default=False, invisible=1)
    user_id = fields.Many2one('res.users', string='Assigned Person')
    washing_date = fields.Datetime(string='Date')
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')
    laundry_obj = fields.Many2one('laundry.order.line', invisible=1)
    product_line = fields.One2many('wash.order.line', 'wash_obj',
                                   string='Products', ondelete='cascade')
    total_amount = fields.Float(compute='get_total', string='Grand Total')

    washing_cancel_remarks = fields.Text(string='Washing Cancel Remarks')
    washing_cancel_remarks_2 = fields.Text(string='Washing Cancel Remarks')

    def hotel_landry_cancel(self):
        view_id = self.env['washing.order.cancel']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hotel Management Washing Order Cancel Remarks',
            'res_model': 'washing.order.cancel',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('laundry_management.landry_washing_cancel_remarks_wizard', False).id,
            'target': 'new',
        }

    def cancel_washing_order(self):
        self.state = 'cancel'


class SaleOrderInherit(models.Model):
    _name = 'wash.order.line'

    @api.depends('price_unit', 'quantity')
    def compute_amount(self):
        total = 0
        for obj in self:
            total += obj.price_unit * obj.quantity
        obj.subtotal = total

    wash_obj = fields.Many2one('washing.washing', string='Order Reference',
                               ondelete='cascade')
    name = fields.Text(string='Description', required=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure ', required=True)
    quantity = fields.Integer(string='Quantity')
    product_id = fields.Many2one('product.product', string='Product')
    price_unit = fields.Float('Unit Price', default=0.0,
                              related='product_id.list_price')
    subtotal = fields.Float(compute='compute_amount', string='Subtotal',
                            readonly=True, store=True)


class LaundryManagementInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        context = self._context
        if context.get('laundry_sale_obj'):
            sale_orders = self.env['sale.order'].browse(
                context.get('laundry_sale_obj'))
        else:
            sale_orders = self.env['sale.order'].browse(
                self._context.get('active_ids', []))
        if self.advance_payment_method == 'delivered':
            sale_orders._create_invoices()
        elif self.advance_payment_method == 'all':
            sale_orders._create_invoices()(final=True)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.values'].sudo().set_default(
                    'sale.config.settings', 'deposit_product_id_setting',
                    self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_(
                        'The product used to invoice a down payment should have an invoice policy set to "Ordered'
                        ' quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_(
                        "The product used to invoice a down payment should be of type 'Service'. Please use another "
                        "product or update this product."))
                taxes = self.product_id.taxes_id.filtered(
                    lambda
                        r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids
                so_line = sale_line_obj.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'tax_id': [(6, 0, tax_ids)],
                })
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _create_invoice(self, order, so_line, amount):
        if (
                self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (
                self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(
                _('The value of the down payment amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.fixed_amount
            name = _('Down Payment')

        invoice_vals = {
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'invoice_payment_ref': order.client_order_ref,
            'invoice_payment_term_id': order.payment_term_id.id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }
        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
        invoice = self.env['account.move'].create(invoice_vals)
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice,
                                               'origin': order},
                                       subtype_id=self.env.ref(
                                           'mail.mt_note').id)
        return invoice


class HotelFolio(models.Model):
    _inherit = "hotel.folio"
    _order = "reservation_id desc"

    reservation_id = fields.Many2one(
        "hotel.reservation", "Reservation", ondelete="restrict"
    )
    hotel_laundry_orders = fields.One2many(
        "laundry.details.line", 'proforma_id'
    )


class LaundryDetails(models.Model):
    _name = 'laundry.details.line'
    _description = 'Laundry Details'

    proforma_id = fields.Many2one('hotel.folio')
    name = fields.Char(string="Label", copy=False)
    partner_id = fields.Many2one('res.partner', string='Guest')
    order_date = fields.Datetime(string="Date")
    laundry_person = fields.Many2one('res.users', string='Laundry Person')
    total_amount = fields.Float(string='Total')


class HotelButtonBox(models.Model):
    _inherit = "hotel.room"

    user_laundary_count = fields.Integer(string="Laundry", compute='get_use_laundry_count')

    def get_use_laundry_count(self):
        self.user_laundary_count = self.env['laundry.order'].sudo().search_count([
            ('hotel_laundary_room_id.name', '=', self.name)])

    def smart_laundry_button_count(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('laundry_management.laundry_order_form_view')
        tree_view = self.sudo().env.ref('laundry_management.laundry_order_tree_view')
        return {
            'name': _(' Laundry Order'),
            'res_model': 'laundry.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('hotel_laundary_room_id.name', '=', self.name)],
        }
