# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date


class BoutiqueOrder(models.Model):
    _name = 'boutique.order'
    _description = 'Boutique Order Details'

    def _get_stock_type_ids(self):
        data = self.env['stock.picking.type'].search([])
        for line in data:
            if line.code == 'outgoing':
                return line

    bill_number = fields.Char(string="Bill No")
    name = fields.Char(string='Reference', copy=False, readonly=True,
                       default=lambda self: _('NB/'))
    booking_date = fields.Date(string="Booking Date")
    delivery_date = fields.Date(string="Delivery Date")
    product_id = fields.Many2many('product.product', string='Product')
    partner_id = fields.Many2one('res.partner', string="Customer")
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      default=_get_stock_type_ids,
                                      help="This will determine picking type of incoming shipment")
    stock_picking_id = fields.Many2one('stock.picking', string="Delivery Reference ", copy=False)
    picking_count = fields.Integer(string="Count", copy=False, compute='_compute_picking_count')
    invoice_count = fields.Integer(string="Count", copy=False, compute='_compute_invoice_count')
    advance_payment_count = fields.Integer(string="Count", copy=False, compute='_compute_invoice_advance_amount_count')
    move_type = fields.Selection([('direct', 'Partial'), ('one', 'All at once')], 'Receive Method', tracking=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)], 'cancel': [('readonly', True)]},
                                 help="It specifies goods to be deliver partially or all at once")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', help="default warehouse where inward will be taken",
                                   readonly=True,
                                   states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    notes = fields.Text(string='Notes')
    boutique_invoice_id = fields.Many2one('account.move', string='Invoice Reference')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('shipped', 'Shipment Sent'),
        ('shipped_done', 'Shipment Done'),
        ('invoiced', 'Invoiced'),
        ('payment_due', 'Payment Due'),
        ('payment_done', 'Payment Done'),
        ('done', 'Closed'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled')], default="draft", string="Status", required="True")
    customer_type = fields.Selection([
        ('walk_in', 'Walk In Customer'),
        ('regular', 'Regular Customer')], default="regular", string="Customer Type")
    customer_phone_number = fields.Char(string='Mobile Number', related='partner_id.mobile')
    duration = fields.Integer(string='Duration')
    received_date = fields.Date(string="Received Date")
    remarks = fields.Text(string="Delivery Remarks")
    saree_type = fields.Selection([
        ('hand', 'Hand Falls'),
        ('machine', 'Machine Falls')], string="Saree Type")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    boutique_ids = fields.One2many('boutique.order.line',
                                   'boutique_order_id',
                                   string="Boutique Measurement")
    boutique1_ids = fields.One2many('boutique.order.line1',
                                    'boutique_order_id',
                                    string="Boutique Measurement")
    boutique2_ids = fields.One2many('boutique.order.line2',
                                    'boutique_order_id',
                                    string="Boutique Measurement")
    boutique_product_ids = fields.One2many('boutique.product.line',
                                           'boutique_product_id',
                                           string="Boutique Measurement")

    boutique_feature_ids = fields.One2many('boutique.measurement',
                                           'boutique_product_id',
                                           string="Boutique Measurement")
    digital_signature = fields.Binary(string="Signature")
    draw_pattern = fields.Html('Draw Boutique Design')
    advanced_payment = fields.Float(string="Advanced Amount")
    received_payment = fields.Float(string="Received Amount")
    balance_payment = fields.Float(string="Balance Amount")
    payment_id = fields.Many2one('account.payment', string='Payment Reference')
    journal_id = fields.Many2one('account.journal', string='Journal')
    journal_type = fields.Selection([
        ('bank', 'Bank'),
        ('cash', 'Cash')], string="Journal Type")

    def create_advance_payment(self):
        hotel_advance_pay = self.env["account.payment"]
        for value in self:
            rec = hotel_advance_pay.sudo().create(
                {
                    "payment_type": 'inbound',
                    "partner_id": value.partner_id.id,
                    "amount": value.advanced_payment,
                    "journal_id": value.journal_id.id,
                    "boutique_id": value.id,
                    "date": fields.Datetime.now(),
                }
            )
            journal = self.env['account.payment'].sudo().search([
                ('boutique_id', '=', value.id),
            ])
            journal.action_post()
            self.write({
                'payment_id': journal.id,
            })

    @api.onchange('journal_type')
    def onchange_journal_type(self):
        journal = self.env['account.journal'].search([('type', '=', self.journal_type)])
        self.write({
            'journal_id': journal.id,
        })

    @api.onchange('duration')
    def onchange_duration(self):
        if self.booking_date:
            my_str = str(self.booking_date)  # 👉️ (mm-dd-yyyy)
            date_1 = datetime.strptime(my_str, '%Y-%m-%d')
            result_1 = date_1 + timedelta(days=self.duration)
            self.write({
                'delivery_date': result_1,
            })

    # @api.onchange("product_id")
    def onchange_boutique_id(self):
        b_list = []
        self.write({'boutique_ids': False})
        product_ids = self.env['product.product'].search([('id', '=', self.product_id.ids)])
        if product_ids and self.product_id:
            for product in product_ids:
                b_list = [[0, 0, {
                    'name': product.name,
                    'display_type': 'line_section',
                }]]
                for line in product.boutique_id:
                    b_list.append([0, 0, {
                        'product_id': line.product_id.id,
                        'boutique_uom': line.uom_id.id,
                        'boutique_measurement': line.measurement,
                        'boutique_name': line.boutique_feature_id.name,
                    }])
                self.write({'boutique_ids': b_list})

    @api.onchange('delivery_date')
    def get_delivery_date(self):
        if self.delivery_date:
            if self.delivery_date <= self.booking_date:
                raise ValidationError("Alert!,Mr. %s. The Boutique Order of %s, "
                                      "Delivery Date should be Greater than "
                                      "Booking Date." \
                                      % (self.env.user.name, self.name))

    @api.onchange('booking_date')
    def get_booking_date(self):
        today = date.today()
        if self.booking_date:
            if self.booking_date < today:
                raise ValidationError("Alert!,Mr. %s. The Boutique Order of %s, "
                                      "Booking Date should not be less than "
                                      "Today." \
                                      % (self.env.user.name, self.name))

    def _compute_picking_count(self):
        self.picking_count = self.env['stock.picking'].sudo().search_count(
            [('origin', '=', self.name)])

    def _compute_invoice_count(self):
        self.invoice_count = self.env['account.move'].sudo().search_count(
            [('payment_reference', '=', self.name)])

    def _compute_invoice_advance_amount_count(self):
        self.advance_payment_count = self.env['account.payment'].sudo().search_count(
            [('boutique_id', '=', self.id)])

    def get_boutique_picking(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('stock.view_picking_form')
        tree_view = self.sudo().env.ref('stock.vpicktree')
        return {
            'name': _('Boutique Picking ID'),
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('origin', '=', self.name)],
        }

    def get_boutique_invoice(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('account.view_move_form')
        tree_view = self.sudo().env.ref('account.view_out_invoice_tree')
        return {
            'name': _('Boutique Picking ID'),
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('payment_reference', '=', self.name)],
        }

    def get_boutique_invoice_advance_payment(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('account.view_account_payment_form')
        tree_view = self.sudo().env.ref('account.view_account_payment_tree')
        return {
            'name': _('Boutique Advance Payment'),
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('boutique_id', '=', self.id)],
        }

    def confirm_boutique(self):
        if not self.boutique_ids:
            raise UserError('Alert!The Boutique Order cannot be confirmed without Line Items, Please check it')
        else:
            self.write({'state': 'confirm'})

    def cancel_boutique(self):
        self.write({'state': 'cancel'})

    def reject_boutique(self):
        self.write({'state': 'reject'})

    def set_draft_boutique(self):
        self.write({'state': 'draft'})

    def get_line_items(self):
        line_vals = []
        picking = self.env['stock.picking']
        for line in self.product_id:
            if line:
                vals = [0, 0, {
                    'name': line.name or '',
                    'product_id': line.id,
                    'product_uom': line.uom_id.id,
                    # 'location_id': picking.picking_type_id.default_location_src_id.id,
                    'location_id': 8,
                    'location_dest_id': self.partner_id.property_stock_customer.id,
                }]
                line_vals.append(vals)
        return line_vals

    def action_stock_move(self):
        if not self.picking_type_id:
            raise UserError(_(
                " Alert!, Please select a picking type"))
        for order in self:
            if not order.stock_picking_id:
                pick = {}
                if order.picking_type_id.code == 'outgoing':
                    pick = {
                        'picking_type_id': order.picking_type_id.id,
                        'partner_id': order.partner_id.id,
                        'origin': order.name,
                        'location_dest_id': order.partner_id.id,
                        'location_id': order.picking_type_id.default_location_src_id.id,
                        'move_type': 'direct',
                        'move_ids_without_package': self.get_line_items(),
                    }
                picking = order.env['stock.picking'].create(pick)
                picking.action_confirm()
                order.write({
                    'state': 'shipped',
                    'stock_picking_id': picking.id
                })

    def get_invoice_line_items(self):
        line_vals = []
        # picking = self.env['account.move']
        for line in self.product_id:
            if line:
                vals = [0, 0, {
                    'name': line.name or '',
                    'product_id': line.id,
                    'quantity': 1,
                    'product_uom_id': line.uom_id.id,
                }]
                line_vals.append(vals)
        return line_vals

    # def create_boutique_customer_invoice(self):
    #     current_user = self.env.uid
    #     # if self.move_type == 'out_invoice':
    #     customer_journal_id = self.env['ir.config_parameter'].sudo().get_param(
    #         'boutique_management.customer_journal_id') or False
    #     invoice = self.env['account.move'].create({
    #         'move_type': 'out_invoice',
    #         'invoice_origin': self.name,
    #         'invoice_user_id': current_user,
    #         'narration': self.name,
    #         'partner_id': self.partner_id.id,
    #         'currency_id': self.env.user.company_id.currency_id.id,
    #         'journal_id': 1,
    #         'payment_reference': self.name,
    #         'ref': self.name,
    #         'l10n_in_gst_treatment': 'unregistered',
    #         'invoice_line_ids': self.get_invoice_line_items(),
    #     })
    #     self.write({
    #         'state': 'payment_due',
    #         'boutique_invoice_id': invoice.id
    #     })
    #     return invoice

    @api.model
    def create(self, vals):
        if vals.get('name', 'NB/') == 'NB/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'boutique.order') or 'NB/'
        return super(BoutiqueOrder, self).create(vals)


# class AccountMove(models.Model):
#     _inherit = "account.move"
#
#     def action_post(self):
#         for line in self.invoice_line_ids:
#             if line.price_unit == 0.00:
#                 raise UserError(_(
#                     " Alert!,The Boutique Invoice cannot be validated without Price for Line items, Please check it."))
#         res = super(AccountMove, self).action_post()
#         return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_type = fields.Selection([
        ('walk_in', 'New Customer'),
        ('regular', 'Regular Customer')], default="regular", string="Customer Type")
    walk_in_customer_phone_number = fields.Char(string='New Customer Mobile Number')
    walk_in_customer_name = fields.Char(string='New Customer Name')
    customer_phone_number = fields.Char(string='Mobile Number', related='partner_id.mobile')
    notes = fields.Text(string='Notes')
    booking_date = fields.Date(string="Booking Date")
    duration = fields.Integer(string='Duration')
    received_date = fields.Date(string="Received Date")
    remarks = fields.Text(string="Delivery Remarks")
    advanced_payment = fields.Float(string="Advanced Amount")
    received_payment = fields.Monetary(string="Invoice Received Amount",
                                       compute='get_received_amount', store=True)
    balance_payment = fields.Monetary(string="Open Balance Amount",
                                      related='invoice_id.amount_residual',
                                      )
    paid_invoice_payment = fields.Monetary(string="Invoice Total Amount",
                                           related='invoice_id.amount_total',
                                           )
    # residual = fields.Monetary(related="invoice_id.amount_residual", string='Open Balance')
    payment_id = fields.Many2one('account.payment', string='Payment Reference')
    journal_id = fields.Many2one('account.journal', string='Journal')
    journal_type = fields.Selection([
        ('bank', 'Bank'),
        ('cash', 'Cash'),
        ('no_cash', 'No Cash')
    ], string="Payment Type", default='no_cash')
    boutique_ids = fields.One2many('boutique.order.line',
                                   'sale_order_id',
                                   string="Boutique Measurement")
    generate_walk_in_customer = fields.Boolean(string='Generate As Regular Customer')
    advance_payment_count = fields.Integer(string="Count", copy=False,
                                           compute='_compute_invoice_advance_amount_count')
    state = fields.Selection(selection_add=[
        ('draft', 'Boutique Quotation'),
        ('sent', 'Boutique Quotation Sent'),
        ('sale', 'Boutique Order'),
        ('done', 'Boutique Closed'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, tracking=True)
    duration = fields.Integer(string='Duration')
    draw_pad = fields.Text(string="Draw Pad")
    invoice_id = fields.Many2one('account.move', string='Invoice Reference')
    stock_picking_id = fields.Many2one('stock.picking', string="Delivery Reference ", copy=False)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    embroidery_boolean = fields.Boolean(string='IS Quotation Embroidery Required')
    advanced_payment_date = fields.Datetime(string="Advanced Payment Date")
    generated_measurement = fields.Boolean(string="Product Measurement Generated")

    @api.depends('balance_payment', 'paid_invoice_payment')
    def get_received_amount(self):
        for rec in self:
            received = 0.00
            if rec.balance_payment and rec.paid_invoice_payment:
                received = rec.paid_invoice_payment - rec.balance_payment
                rec.received_payment = received
            else:
                rec.received_payment = received

    @api.onchange('duration')
    def onchange_duration(self):
        if self.booking_date:
            my_str = str(self.booking_date)  # 👉️ (mm-dd-yyyy)
            date_1 = datetime.strptime(my_str, '%Y-%m-%d')
            result_1 = date_1 + timedelta(days=self.duration)
            self.write({
                'commitment_date': result_1,
            })

    # def create_invoices(self):
    #     self.write(
    #         {'invoice_id': self.invoice_id.id}
    #     )

    def create_advance_payment(self):
        hotel_advance_pay = self.env["account.payment"]
        for value in self:
            if value.advanced_payment > 0.00:
                rec = hotel_advance_pay.create(
                    {
                        "payment_type": 'inbound',
                        "partner_id": value.partner_id.id,
                        "amount": value.advanced_payment,
                        "journal_id": value.journal_id.id,
                        "boutique_id": value.id,
                        "date": fields.Datetime.now(),
                    }
                )
                journal = self.env['account.payment'].search([
                    ('boutique_id', '=', value.id),
                ])
                journal.action_post()
                self.write({
                    'payment_id': journal.id,
                    'advanced_payment_date': fields.Datetime.now(),
                })
            else:
                raise ValidationError(
                    _('Alert !!  Mr.%s - You cannot create Advance Payment with Zero Value'
                      ' for Boutique Quotation of %s.Please Check it.') % (value.user_id.name, value.name))

    @api.onchange('generate_walk_in_customer')
    def create_new_transfer_contract(self):
        if self.generate_walk_in_customer:
            customer = self.sudo().env['res.partner'].sudo().create({
                'name': self.walk_in_customer_name,
                'mobile': self.walk_in_customer_phone_number,
            })
            existing_customer_record = self.sudo().env['res.partner']. \
                sudo().search([('name', '=', self.walk_in_customer_name),
                               ('mobile', '=', self.walk_in_customer_phone_number)])
            self.write({'partner_id': existing_customer_record.id,
                        'customer_type': 'regular'})

    @api.onchange('booking_date')
    def get_booking_date(self):
        today = date.today()
        if self.booking_date:
            if self.booking_date < today:
                raise ValidationError("Alert!,Mr. %s. The Boutique Order of %s, "
                                      "Booking Date should not be less than "
                                      "Today." \
                                      % (self.env.user.name, self.name))

    @api.onchange('validity_date')
    def get_booking_date(self):
        today = date.today()
        if self.booking_date:
            if self.validity_date <= today:
                raise ValidationError("Alert!,Mr. %s. The Boutique Order of %s, "
                                      "Boutique Expire Date should Greater than Today"
                                      % (self.env.user.name, self.name))

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for val in self:
            if not val.order_line:
                raise ValidationError('Alert!!, Mr.%s, Please Add Products in the %s - Boutique Order Line to Confirm '
                                      'the Order.' % (self.env.user.name, self.name))
            if val.order_line:
                for price in val.order_line:
                    if price.price_unit == 0.00:
                        raise ValidationError(
                            'Alert!!, Mr.%s,  Add the %s - Boutique Order Line Products Unit Price and Confirm the '
                            'Order.' % (self.env.user.name, self.name))
            picking = self.env['stock.picking'].search([('origin', '=', self.name)])
            if picking:
                val.write({
                    'stock_picking_id': picking.id,
                })
        return res

    def onchange_boutique_id(self):
        b_list = []
        self.write({'boutique_ids': False})
        product_ids = self.env['product.product'].search([('id', '=', self.order_line.product_id.ids)])
        if product_ids and self.order_line.product_id.ids:
            for product in product_ids:
                b_list = [[0, 0, {
                    'name': product.display_name,
                    'display_type': 'line_section',
                }]]
                for line in product.boutique_id:
                    b_list.append([0, 0, {
                        'product_id': line.product_id.id,
                        'boutique_uom': line.uom_id.id,
                        'boutique_measurement': line.measurement,
                        'boutique_name': line.boutique_feature_id.name,
                    }])
                self.write({'boutique_ids': b_list})

    @api.onchange('journal_type')
    def onchange_journal_type(self):
        journal = self.env['account.journal'].search([('type', '=', self.journal_type)])
        self.write({
            'journal_id': journal.id,
        })

    def _compute_invoice_advance_amount_count(self):
        self.advance_payment_count = self.env['account.payment'].sudo().search_count(
            [('boutique_id', '=', self.id)])

    def get_boutique_invoice_advance_payment(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('account.view_account_payment_form')
        tree_view = self.sudo().env.ref('account.view_account_payment_tree')
        return {
            'name': _('Boutique Advance Payment'),
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('boutique_id', '=', self.id)],
        }


class BoutiqueOrderLine(models.Model):
    _name = 'boutique.order.line'
    _description = 'Boutique Order Details'

    boutique_order_id = fields.Many2one('sale.order', string='Product')
    boutique_uom = fields.Many2one('uom.uom', string='Boutique UOM')
    boutique_measurement = fields.Float(string='Boutique Measurement')
    boutique_name = fields.Char(string='Boutique name')
    remark_notes = fields.Text(string='Patterns')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string="Name", invisible=True)
    sequence = fields.Integer(default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sale_order_id = fields.Many2one('sale.order', string="Sale Id")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sales Order Line'

    attached_image_ref = fields.Binary(string="Attach Image Ref")


class BoutiqueOrderline1(models.Model):
    _name = 'boutique.order.line1'
    _description = 'Boutique Order Details 1'

    boutique_order_id = fields.Many2one('boutique.order', string='Product ')
    boutique_uom = fields.Many2one('uom.uom', string='Boutique UOM')
    boutique_measurement = fields.Char(string='Boutique Measurement')
    boutique_name = fields.Char(string='Boutique name')
    remark_notes = fields.Text(string='Patterns')
    product_id = fields.Many2one('product.product', string='Product')


class BoutiqueOrderLine2(models.Model):
    _name = 'boutique.order.line2'
    _description = 'Boutique Order Details 2'

    boutique_order_id = fields.Many2one('boutique.order', string='Product ')
    boutique_uom = fields.Many2one('uom.uom', string='Boutique UOM')
    boutique_measurement = fields.Char(string='Boutique Measurement')
    boutique_name = fields.Char(string='Boutique name')
    remark_notes = fields.Text(string='Patterns')
    product_id = fields.Many2one('product.product', string='Product')


class BoutiqueProductLine(models.Model):
    _name = 'boutique.product.line'
    _description = 'Boutique Product Details'

    boutique_product_id = fields.Many2one('boutique.order', string='Product')
    product_id = fields.Many2one('product.product', string='Product')
    product_order = fields.Boolean(string='Order')
