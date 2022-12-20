# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HotelBarTables(models.Model):
    _name = "hotel.bar.tables"
    _description = "Includes Hotel Restaurant Table"

    name = fields.Char("Table Number", required=True)
    capacity = fields.Integer("Capacity")

    @api.constrains('name')
    def _check_table_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                code = self.sudo().search(domain)
                if len(code) > 1:
                    for i in range(len(code)):
                        if code[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  The Table Name of - %s is already exists.\n'
                                  'Please check it.....') % (
                                    record.name))


class HotelBarReservation(models.Model):
    _name = "hotel.bar.reservation"
    _description = "Hotel Bar Reservation"
    _rec_name = "reservation_id"

    def create_order(self):
        """
        This method is for create a new order for hotel restaurant
        reservation .when table is booked and create order button is
        clicked then this method is called and order is created.you
        can see this created order in "Orders"
        ------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel restaurant reservation.
        """
        reservation_order = self.env["hotel.bar.order"]
        for record in self:
            table_ids = record.table_nos_ids.ids
            values = {
                "reservation_id": record.id,
                "order_date": record.start_date,
                "folio_id": record.folio_id.id,
                "table_nos_ids": [(6, 0, table_ids)],
                "is_folio": record.is_folio,
            }
            reservation_order.create(values)
        self.write({"state": "order"})
        return True

    @api.onchange("customer_id")
    def _onchange_partner_id(self):
        """
        When Customer name is changed respective adress will display
        in Adress field
        @param self: object pointer
        """
        if not self.customer_id:
            self.partner_address_id = False
        else:
            addr = self.customer_id.address_get(["default"])
            self.partner_address_id = addr["default"]

    @api.onchange("folio_id")
    def _onchange_folio_id(self):
        """
        When you change folio_id, based on that it will update
        the customer_id and room_number as well
        ---------------------------------------------------------
        @param self: object pointer
        """
        for rec in self:
            if rec.folio_id:
                rec.customer_id = rec.folio_id.partner_id.id
                rec.room_id = rec.folio_id.room_line_ids[0].product_id.id

    def action_set_to_draft(self):
        """
        This method is used to change the state
        to draft of the hotel restaurant reservation
        --------------------------------------------
        @param self: object pointer
        """
        self.write({"state": "draft"})

    def table_reserved(self):
        """
        when CONFIRM BUTTON is clicked this method is called for
        table reservation
        @param self: The object pointer
        @return: change a state depending on the condition
        """

        for reservation in self:
            if not reservation.table_nos_ids:
                raise ValidationError(_("Please Select Tables For Reservation"))
            reservation._cr.execute(
                "select count(*) from "
                "hotel_bar_reservation as hrr "
                "inner join bar_table as rt on \
                             rt.bar_table_id = hrr.id "
                "where (start_date,end_date)overlaps\
                             ( timestamp %s , timestamp %s ) "
                "and hrr.id<> %s and state != 'done'"
                "and rt.name in (select rt.name from \
                             hotel_bar_reservation as hrr "
                "inner join bar_table as rt on \
                             rt.bar_table_id = hrr.id "
                "where hrr.id= %s) ",
                (
                    reservation.start_date,
                    reservation.end_date,
                    reservation.id,
                    reservation.id,
                ),
            )
            res = self._cr.fetchone()
            roomcount = res and res[0] or 0.0
            if roomcount:
                raise ValidationError(
                    _(
                        """You tried to confirm reservation """
                        """with table those already reserved """
                        """in this reservation period"""
                    )
                )
            reservation.state = "confirm"
        return True

    def table_cancel(self):
        """
        This method is used to change the state
        to cancel of the hotel restaurant reservation
        --------------------------------------------
        @param self: object pointer
        """
        self.write({"state": "cancel"})

    def table_done(self):
        """
        This method is used to change the state
        to done of the hotel restaurant reservation
        --------------------------------------------
        @param self: object pointer
        """
        self.write({"state": "done"})

    reservation_id = fields.Char("Reservation No", readonly=True, index=True)
    room_id = fields.Many2one("hotel.reservation", "Room No")
    folio_id = fields.Many2one("hotel.folio", "Folio No")
    start_date = fields.Datetime(
        "Start Time", required=True, default=lambda self: fields.Datetime.now()
    )
    end_date = fields.Datetime("End Time", required=True)
    customer_id = fields.Many2one("res.partner", "Guest Name", required=True)
    partner_address_id = fields.Many2one("res.partner", "Address")
    table_nos_ids = fields.Many2many(
        "hotel.bar.tables",
        "bar_table",
        "bar_table_id",
        "name",
        string="Table Number",
        help="Table reservation detail.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("order", "Order Created"),
        ],
        "State",
        required=True,
        readonly=True,
        copy=False,
        default="draft",
    )
    is_folio = fields.Boolean("Is a Hotel Guest??")

    table_cancel_remarks = fields.Text(string='Table Cancel Remarks')
    table_cancel_remarks_2 = fields.Text(string='Table Cancel Remarks')

    @api.onchange('room_id')
    def fetch_name(self):
        self.customer_id = self.room_id.partner_id

    def hotel_management_table_cancel(self):
        view_id = self.env['hotel.management.table.cancel']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hotel Management Table Cancel Remarks',
            'res_model': 'hotel.management.table.cancel',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('hotel_bar.hotel_management_table_cancel_remarks_wizard', False).id,
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        seq_obj = self.env["ir.sequence"]
        reserve = seq_obj.next_by_code("hotel.bar.reservation") or "New"
        vals["reservation_id"] = reserve
        return super(HotelBarReservation, self).create(vals)

    @api.constrains("start_date", "end_date")
    def _check_start_dates(self):
        """
        This method is used to validate the start_date and end_date.
        -------------------------------------------------------------
        @param self: object pointer
        @return: raise a warning depending on the validation
        """
        if self.start_date >= self.end_date:
            raise ValidationError(_("Start Date Should be less than the End Date!"))
        if self.is_folio:
            for line in self.folio_id.room_line_ids:
                if self.start_date < line.checkin_date:
                    raise ValidationError(
                        _(
                            """Start Date Should be greater """
                            """than the Folio Check-in Date!"""
                        )
                    )
                if self.end_date > line.checkout_date:
                    raise ValidationError(
                        _("End Date Should be less than the Folio Check-out Date!")
                    )


class HotelBarOrder(models.Model):
    _name = "hotel.bar.order"
    _description = "Hotel Bar Order"
    _rec_name = "order_number"

    @api.depends("order_list_ids")
    def _compute_amount_all_total(self):
        """
        amount_subtotal and amount_total will display on change of order_list_ids
        ---------------------------------------------------------------------
        @param self: object pointer
        """
        for sale in self:
            sale.amount_subtotal = sum(
                line.price_subtotal for line in sale.order_list_ids
            )
            sale.amount_total = (
                    sale.amount_subtotal + (sale.amount_subtotal * sale.tax) / 100
            )

    def reservation_generate_kot(self):
        """
        This method create new record for hotel restaurant order list.
        --------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel restaurant order list.
        """
        res = []
        order_tickets_obj = self.env["hotel.restaurant.kitchen.order.tickets"]
        rest_order_list_obj = self.env["hotel.bar.order.list"]

        for order in self:
            if not order.order_list_ids:
                raise ValidationError(_("Please Give an Order"))
            table_ids = order.table_nos_ids.ids
            line_data = {
                "order_number": order.order_number,
                # "reservation_number": order.reservation_id.reservation_id,
                "kot_date": order.order_date,
                "waiter_name": order.waitername.name,
                "table_nos_ids": [(7, 0, table_ids)],
            }
            kot_data = order_tickets_obj.create(line_data)
            for order_line in order.order_list_ids:
                o_line = {
                    "kot_order_id": kot_data.id,
                    "menucard_id": order_line.menucard_id.id,
                    "item_qty": order_line.item_qty,
                    "item_rate": order_line.item_rate,
                }
                rest_order_list_obj.create(o_line)
                res.append(order_line.id)
            order.update(
                {
                    "kitchen": kot_data.id,
                    "rests_ids": [(7, 0, res)],
                    "state": "order",
                }
            )
        return res

    def reservation_update_kot(self):
        """
        This method update record for hotel restaurant order list.
        ----------------------------------------------------------
        @param self: The object pointer
        @return: update record set for hotel restaurant order list.
        """

        order_tickets_obj = self.env["hotel.restaurant.kitchen.order.tickets"]
        rest_order_list_obj = self.env["hotel.bar.order.list"]
        for order in self:
            table_ids = order.table_nos_ids.ids
            line_data = {
                "order_number": order.order_number,
                "reservation_number": order.reservation_id.reservation_id,
                "kot_date": fields.Datetime.to_string(fields.datetime.now()),
                "waiter_name": order.waitername.name,
                "table_nos_ids": [(7, 0, table_ids)],
            }
            kot_id = order_tickets_obj.browse(self.kitchen)
            kot_id.write(line_data)
            for order_line in order.order_list_ids:
                if order_line not in order.rests_ids.ids:
                    kot_data = order_tickets_obj.create(line_data)
                    o_line = {
                        "kot_order_id": kot_data.id,
                        "menucard_id": order_line.menucard_id.id,
                        "item_qty": order_line.item_qty,
                        "item_rate": order_line.item_rate,
                    }
                    order.update(
                        {
                            "kitchen": kot_data.id,
                            "rests_ids": [(5, order_line.id)],
                        }
                    )
                    rest_order_list_obj.create(o_line)
        return True

    def done_kot(self):
        """
        This method is used to change the state
        to done of the hotel reservation order
        ----------------------------------------
        @param self: object pointer
        """

        hsl_obj = self.env["hotel.service.line"]
        so_line_obj = self.env["sale.order.line"]
        for res_order in self:
            for order in res_order.order_list_ids:
                if res_order.folio_id:
                    values = {
                        "order_id": res_order.folio_id.order_id.id,
                        "name": order.menucard_id.name,
                        "product_id": order.menucard_id.product_id.id,
                        "product_uom_qty": order.item_qty,
                        "price_unit": order.item_rate,
                        "price_subtotal": order.price_subtotal,
                    }
                    sol_rec = so_line_obj.create(values)
                    hsl_obj.create(
                        {
                            "folio_id": res_order.folio_id.id,
                            "service_line_id": sol_rec.id,
                        }
                    )
                    res_order.folio_id.write(
                        {"hotel_bar_orders_ids": [(4, res_order.id)]}
                    )
                    res_order.reservation_id.write({"state": "done"})
                self.write({"state": "done"})
                return True

    order_number = fields.Char("Order No", readonly=True)
    reservation_id = fields.Many2one("hotel.reservation", "Reservation ID")
    order_date = fields.Datetime(
        "Date", required=True, default=lambda self: fields.Datetime.now()
    )
    waitername = fields.Many2one("res.partner", "Waiter Name")
    table_nos_ids = fields.Many2many(
        "hotel.bar.tables",
        "temp_table5",
        "table_bar_no",
        "name",
        "Table Number",
    )

    order_list_ids = fields.One2many(
        "hotel.bar.order.list", "reservation_order_id", "Order List"
    )
    tax = fields.Float("Tax (%) ")
    amount_subtotal = fields.Float(
        compute="_compute_amount_all_total", string="Subtotal"
    )
    amount_total = fields.Float(compute="_compute_amount_all_total", string="Total")
    kitchen = fields.Integer("Kitchen Id")
    rests_ids = fields.Many2many(
        "hotel.bar.order.list",
        "reservation_id",
        "kitchen_bar_id",
        "res_bar_ids",
        "Rest",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("order", "Order Created"), ("done", "Done"), ("cancel", "Cancel")],
        "State",
        required=True,
        readonly=True,
        default="draft",
    )
    folio_id = fields.Many2one("hotel.folio", "Folio No")
    is_folio = fields.Boolean(
        "Is a Hotel Guest??", help="is guest reside in hotel or not"
    )

    order_cancel_remarks = fields.Text(string='Order Cancel Remarks')
    order_cancel_remarks_2 = fields.Text(string='Order Cancel Remarks')

    @api.onchange('reservation_id')
    def fetch_folio_id(self):
        id = self.env['hotel.folio'].sudo().search([
            ('reservation_id', '=', self.reservation_id.id)])
        for i in id:
            if self.reservation_id:
                self.folio_id = i.id

    def hotel_management_order_cancel(self):
        view_id = self.env['hotel.management.order.cancel']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hotel Management Orders Cancel Remarks',
            'res_model': 'hotel.management.order.cancel',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('hotel_restaurant.hotel_management_order_cancel_remarks_wizard', False).id,
            'target': 'new',
        }

    def order_cancel(self):
        """
        This method is used to change the state
        to cancel of the hotel restaurant reservation
        --------------------------------------------
        @param self: object pointer
        """
        self.write({"state": "cancel"})

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        seq_obj = self.env["ir.sequence"]
        res_oder = seq_obj.next_by_code("hotel.bar.order") or "New"
        vals["order_number"] = res_oder
        return super(HotelBarOrder, self).create(vals)


class HotelBarOrderList(models.Model):
    _name = "hotel.bar.order.list"
    _description = "Includes Hotel Restaurant Order"

    @api.depends("item_qty", "item_rate")
    def _compute_price_subtotal(self):
        """
        price_subtotal will display on change of item_rate
        --------------------------------------------------
        @param self: object pointer
        """
        for line in self:
            line.price_subtotal = line.item_rate * int(line.item_qty)

    @api.onchange("menucard_id")
    def _onchange_item_name(self):
        """
        item rate will display on change of item name
        ---------------------------------------------
        @param self: object pointer
        """
        self.item_rate = self.menucard_id.list_price

    reservation_order_id = fields.Many2one(
        "hotel.bar.order", "Reservation Order"
    )
    kot_order_id = fields.Many2one("hotel.restaurant.kitchen.order.tickets", "Kitchen Order Tickets")
    menucard_id = fields.Many2one("hotel.menucard", "Item Name", required=True)
    item_qty = fields.Integer("Qty", required=True, default=1)
    item_rate = fields.Float("Rate")
    price_subtotal = fields.Float(compute="_compute_price_subtotal", string="Subtotal")

