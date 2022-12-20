# See LICENSE file for full copyright and licensing details.

from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HotelReservation(models.Model):
    _name = "hotel.reservation"
    _rec_name = "reservation_no"
    _description = "Reservation"
    _order = "reservation_no desc"
    _inherit = ["mail.thread"]

    def _compute_folio_count(self):
        for res in self:
            res.update({"no_of_folio": len(res.folio_id.ids)})

    reservation_no = fields.Char("Reservation No", readonly=True, copy=False,
                                 compute='get_reservation_num',
                                 store=True)
    date_order = fields.Datetime(
        "Date Ordered",
        readonly=True,
        required=True,
        index=True,
        default=lambda self: fields.Datetime.now(),
    )

    company_id = fields.Many2one(
        "res.company",
        "Hotel",
        readonly=True,
        index=True,
        required=True,
        default=1,
        states={"draft": [("readonly", False)]},
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Guest Name",
        readonly=True,
        index=True,
        required=True,
        states={"draft": [("readonly", False)]},
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        "Scheme",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Pricelist for current reservation.",
    )
    partner_invoice_id = fields.Many2one(
        "res.partner",
        "Invoice Address",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Invoice address for " "current reservation.",
    )
    partner_order_id = fields.Many2one(
        "res.partner",
        "Ordering Contact",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="The name and address of the "
             "contact that requested the order "
             "or quotation.",
    )
    partner_shipping_id = fields.Many2one(
        "res.partner",
        "Delivery Address",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Delivery address" "for current reservation. ",
    )
    checkin = fields.Datetime(
        "Check In",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    checkout = fields.Datetime(
        "Check Out",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    adults = fields.Integer(
        "Adults",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="List of adults there in guest list. ",
    )
    children = fields.Integer(
        "Children",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Number of children there in guest list.",
    )
    reservation_line = fields.One2many(
        "hotel.reservation.line",
        "line_id",
        string="Reservation Line",
        help="Hotel room reservation details.",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("cancel", "Cancel"),
            ("done", "Done"),
        ],
        "State",
        readonly=True,
        default="draft",
    )
    folio_id = fields.Many2many(
        "hotel.folio",
        "hotel_folio_reservation_rel",
        "order_id",
        "invoice_id",
        string="Proforma",
    )
    no_of_folio = fields.Integer("No. Proforma", compute='_compute_folio_count')
    reservation_cancel_remarks = fields.Text(string='Reservation Cancel Remarks')
    reservation_cancel_remarks2 = fields.Text(string='Reservation Cancel Remarks')
    booking_hrs = fields.Float(string='Hrs', compute='_calculate_hrs', store=True)
    days = fields.Char(string='Days', store=True)
    advance_payment = fields.Float(string="Advance")
    proof_type = fields.Binary(string='Proof')
    days_1 = fields.Float(string='Days', store=True)
    guest_type_nation = fields.Many2one('hotel.guest.type', string='Guest Type')
    booking_source = fields.Many2one('hotel.booking.source', string='Booking Source')
    amount_Receive = fields.Char('Amount state')

    reservation_hrs_selection = fields.Selection([
        ('short', 'Free Hours'),
        ('12', '12 Hours'),
        ('24', '24 Hours'),
    ])
    checkin_checklist_line = fields.One2many(
        "checkin.checklist", "room_reservation")
    @api.onchange('days')
    def days_integer(self):
        if self.days:
            value = str(self.days).split(" ")[0]
            self.days_1 = float(value)
            print("=======================",self.days,value,self.days_1)
        else:
            pass

    @api.depends('checkin', 'checkout')
    @api.onchange('checkin', 'checkout')
    def _calculate_hrs(self):
        if self.checkin and self.checkout:
            date1 = str(self.checkin)
            datetimeFormat = '%Y-%m-%d %H:%M:%S'
            date2 = str(self.checkout)
            date11 = datetime.strptime(date1, datetimeFormat)
            date12 = datetime.strptime(date2, datetimeFormat)
            timedelta = date12 - date11
            tot_sec = timedelta.total_seconds()
            h = tot_sec // 3600
            m = (tot_sec % 3600) // 60
            duration_hour = ("%d.%d" % (h, m))
            self.booking_hrs = float(duration_hour)
            if self.booking_hrs >= 24.00:
                self.days = timedelta
            else:
                self.days = False
            if self.checkin > self.checkout:
                raise ValidationError(_("Alert!,Reference of {self.reservation_id.name} Check Out Date Should be"
                                        "less than the Check In Date"))

    @api.constrains("checkin", "checkout")
    def _check_dates(self):
        if self.checkin > self.checkout:
            raise ValidationError(_(" Check Out Date Should be less than the Check In Date!"))

    def hotel_management_cancel_remarks(self):
        view_id = self.env['hotel.management.cancel.remarks']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hotel Management Cancel Remarks',
            'res_model': 'hotel.management.cancel.remarks',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('hotel_extended.hotel_management_reservation_cancel_remarks_wizard', False).id,
            'target': 'new',
        }

    def room_cancel(self):
        self.state = 'cancel'

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        lines_of_moves_to_post = self.filtered(
            lambda reserv_rec: reserv_rec.state != "draft"
        )
        if lines_of_moves_to_post:
            raise ValidationError(
                _("Sorry, you can only delete the reservation when it's draft!")
            )
        return super(HotelReservation, self).unlink()

    def copy(self):
        ctx = dict(self._context) or {}
        ctx.update({"duplicate": True})
        return super(HotelReservation, self.with_context(ctx)).copy()

    # @api.constrains("reservation_line", "adults", "children")
    def _check_reservation_rooms(self):
        """
        This method is used to validate the reservation_line.
        -----------------------------------------------------
        @param self: object pointer
        @return: raise a warning depending on the validation
        """
        ctx = dict(self._context) or {}
        for reservation in self:
            cap = 0
            for rec in reservation.reservation_line:
                if len(rec.reserve) == 0:
                    raise ValidationError(_("Alert!, Please Select Rooms For Reservation."))
                cap = sum(room.capacity for room in rec.reserve)
            if not ctx.get("duplicate"):
                if (reservation.adults + reservation.children) > cap:
                    raise ValidationError(
                        _(
                            "Alert!, Room Capacity Exceeded \n"
                            " Please Select Rooms According to"
                            " Members Accommodation."
                        )
                    )
            if reservation.adults <= 0:
                raise ValidationError(_("Alert!, Adults must be more than 0"))

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel reservation as well
        ---------------------------------------------------------------------
        @param self: object pointer
        """
        if not self.partner_id:
            self.update(
                {
                    "partner_invoice_id": False,
                    "partner_shipping_id": False,
                    "partner_order_id": False,
                }
            )
        else:
            addr = self.partner_id.address_get(["delivery", "invoice", "contact"])
            self.update(
                {
                    "partner_invoice_id": addr["invoice"],
                    "partner_shipping_id": addr["delivery"],
                    "partner_order_id": addr["contact"],
                    "pricelist_id": self.partner_id.property_product_pricelist.id,
                }
            )

    @api.depends('partner_id')
    @api.onchange('partner_id')
    def get_reservation_num(self):
        print('--------------------------')
        if self.reservation_no:
            for val in self.reservation_line:
                room_code = val.reserve.room_no
                # type_code = val.reserve.room_categ_id.short_code
                floor_code = val.reserve.floor_id.short_code
                self.reservation_no = room_code + '/' + self.reservation_no
            # vals["reservation_no"] = (
            #         self.env["ir.sequence"].next_by_code("hotel.reservation") or "New"
            # )
            # print('***********************************************', res_code)

    @api.model
    def create(self, vals):
        # res = super(HotelReservation, self).create(vals)
        # res.get_reservation_num()
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        vals["reservation_no"] = (
                self.env["ir.sequence"].next_by_code("hotel.reservation") or "New"
        )

        return super(HotelReservation, self).create(vals)

    def check_overlap(self, date1, date2):
        delta = date2 - date1
        return {date1 + timedelta(days=i) for i in range(delta.days + 1)}

    def confirmed_reservation(self):
        """
        This method create a new record set for hotel room reservation line
        -------------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel room reservation line.
        """
        self._check_reservation_rooms()
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        vals = {}
        for reservation in self:
            reserv_checkin = reservation.checkin
            reserv_checkout = reservation.checkout
            room_bool = False
            for line_id in reservation.reservation_line:
                for room in line_id.reserve:
                    if room.room_reservation_line_ids:
                        for reserv in room.room_reservation_line_ids.search(
                                [
                                    ("status", "in", ("confirm", "done")),
                                    ("room_id", "=", room.id),
                                ]
                        ):
                            check_in = reserv.check_in
                            check_out = reserv.check_out
                            if check_in <= reserv_checkin <= check_out:
                                room_bool = True
                            if check_in <= reserv_checkout <= check_out:
                                room_bool = True
                            if (
                                    reserv_checkin <= check_in
                                    and reserv_checkout >= check_out
                            ):
                                room_bool = True
                            r_checkin = reservation.checkin.date()
                            r_checkout = reservation.checkout.date()
                            check_intm = reserv.check_in.date()
                            check_outtm = reserv.check_out.date()
                            range1 = [r_checkin, r_checkout]
                            range2 = [check_intm, check_outtm]
                            overlap_dates = self.check_overlap(
                                *range1
                            ) & self.check_overlap(*range2)
                            if room_bool:
                                raise ValidationError(
                                    _(
                                        "Alert!, You tried to Confirm "
                                        "Reservation with room"
                                        " those already "
                                        "reserved in this "
                                        "Reservation Period. "
                                        "Overlap Dates are "
                                        "%s"
                                    )
                                    % overlap_dates
                                )
                            else:
                                self.state = "confirm"
                                vals = {
                                    "room_id": room.id,
                                    "check_in": reservation.checkin,
                                    "check_out": reservation.checkout,
                                    "state": "assigned",
                                    "reservation_id": reservation.id,
                                }
                                room.write({"isroom": False, "status": "confirm"})
                        else:
                            self.state = "confirm"
                            vals = {
                                "room_id": room.id,
                                "check_in": reservation.checkin,
                                "check_out": reservation.checkout,
                                "state": "assigned",
                                "reservation_id": reservation.id,
                            }
                            room.write({"isroom": False, "status": "confirm"})
                    else:
                        self.state = "confirm"
                        vals = {
                            "room_id": room.id,
                            "check_in": reservation.checkin,
                            "check_out": reservation.checkout,
                            "state": "assigned",
                            "reservation_id": reservation.id,
                        }
                        room.write({"isroom": False, "status": "confirm"})
                    reservation_line_obj.create(vals)
        return True

    def cancel_reservation(self):
        """
        This method cancel record set for hotel room reservation line
        ------------------------------------------------------------------
        @param self: The object pointer
        @return: cancel record set for hotel room reservation line.
        """

        room_res_line_obj = self.env["hotel.room.reservation.line"]
        hotel_res_line_obj = self.env["hotel.reservation.line"]
        self.state = "cancel"
        room_reservation_line = room_res_line_obj.search(
            [("reservation_id", "in", self.ids)]
        )
        room_reservation_line.write({"state": "unassigned"})
        room_reservation_line.unlink()
        reservation_lines = hotel_res_line_obj.search([("line_id", "in", self.ids)])
        for reservation_line in reservation_lines:
            reservation_line.reserve.write({"isroom": True, "status": "available"})
        return True

    #
    def set_to_draft_reservation(self):
        self.update({"state": "draft"})

    #
    def action_send_reservation_mail(self):
        """
        This function opens a window to compose an email,
        template message loaded by default.
        @param self: object pointer
        """
        self.ensure_one(), "This is for a single id at a time."
        template_id = self.env.ref(
            "hotel_extended.email_template_hotel_reservation"
        ).id
        compose_form_id = self.env.ref("mail.email_compose_message_wizard_form").id
        ctx = {
            "default_model": "hotel.reservation",
            "default_res_id": self.id,
            "default_use_template": bool(template_id),
            "default_template_id": template_id,
            "default_composition_mode": "comment",
            "force_send": True,
            "mark_so_as_sent": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
            "force_send": True,
        }

    @api.model
    def reservation_reminder_24hrs(self):
        """
        This method is for scheduler
        every 1day scheduler will call this method to
        find all tomorrow's reservations.
        ----------------------------------------------
        @param self: The object pointer
        @return: send a mail
        """
        now_date = fields.Date.today()
        template_id = self.env.ref(
            "hotel_extended.mail_template_reservation_reminder_24hrs"
        )
        for reserv_rec in self:
            checkin_date = reserv_rec.checkin
            difference = relativedelta(now_date, checkin_date)
            if (
                    difference.days == -1
                    and reserv_rec.partner_id.email
                    and reserv_rec.state == "confirm"
            ):
                template_id.send_mail(reserv_rec.id, force_send=True)
        return True

    def create_folio(self):
        """
        This method is for create new hotel folio.
        -----------------------------------------
        @param self: The object pointer
        @return: new record set for hotel folio.
        """
        value = self.booking_hrs/24.00
        self.days_1 = float(value)
        hotel_folio_obj = self.env["hotel.folio"]
        for reservation in self:
            folio_lines = []
            checkin_date = reservation["checkin"]
            checkout_date = reservation["checkout"]
            duration_vals = self._onchange_check_dates(
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                duration=False,
            )
            duration = duration_vals.get("duration") or 0.0
            folio_vals = {
                "date_order": reservation.date_order,
                "company_id": reservation.company_id.id,
                "partner_id": reservation.partner_id.id,
                "pricelist_id": reservation.pricelist_id.id,
                "partner_invoice_id": reservation.partner_invoice_id.id,
                "partner_shipping_id": reservation.partner_shipping_id.id,
                "checkin_date": reservation.checkin,
                "checkout_date": reservation.checkout,
                "duration": duration,
                "reservation_id": reservation.id,
            }
            for line in reservation.reservation_line:
                for r in line.reserve:
                    folio_lines.append(
                        (
                            0,
                            0,
                            {
                                "checkin_date": checkin_date,
                                "checkout_date": checkout_date,
                                "actual_checkout": checkout_date,
                                "product_id": r.product_id and r.product_id.id,
                                "name": reservation["reservation_no"],
                                "price_unit": r.list_price,
                                "product_uom_qty": self.days_1,
                                "is_reserved": True,
                            },
                        )
                    )
                    r.write({"status": "confirm", "isroom": False})
            folio_vals.update({"room_line_ids": folio_lines})
            folio = hotel_folio_obj.create(folio_vals)
            for rm_line in folio.room_line_ids:
                rm_line._onchange_product_id()
            self.write({"folio_id": [(6, 0, folio.ids)], "state": "done"})
        return True

    def _onchange_check_dates(
            self, checkin_date=False, checkout_date=False, duration=False
    ):
        """
        This method gives the duration between check in checkout if
        customer will leave only for some hour it would be considers
        as a whole day. If customer will checkin checkout for more or equal
        hours, which configured in company as additional hours than it would
        be consider as full days
        --------------------------------------------------------------------
        @param self: object pointer
        @return: Duration and checkout_date
        """
        value = {}
        configured_addition_hours = self.company_id.additional_hours
        duration = 0
        if checkin_date and checkout_date:
            dur = checkout_date - checkin_date
            duration = dur.days + 1
            if configured_addition_hours > 0:
                additional_hours = abs(dur.seconds / 60)
                if additional_hours <= abs(configured_addition_hours * 60):
                    duration -= 1
        value.update({"duration": duration})
        return value

    def open_folio_view(self):
        folios = self.mapped("folio_id")
        action = self.env.ref("hotel.open_hotel_folio1_form_tree_all").read()[0]
        if len(folios) > 1:
            action["domain"] = [("id", "in", folios.ids)]
        elif len(folios) == 1:
            action["views"] = [(self.env.ref("hotel.view_hotel_folio_form").id, "form")]
            action["res_id"] = folios.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action


#
class HotelReservationLine(models.Model):
    _name = "hotel.reservation.line"
    _description = "Reservation Line"

    name = fields.Char("Name")
    line_id = fields.Many2one("hotel.reservation")
    reserve = fields.Many2many(
        "hotel.room",
        "hotel_reservation_line_room_rel",
        "hotel_reservation_line_id",
        "room_id",
        domain="[('isroom','=',True),\
                               ('categ_id','=',categ_id)]",
    )
    categ_id = fields.Many2one("hotel.room.type", "Room Type")

    @api.onchange("categ_id")
    def on_change_categ(self):
        """
        When you change categ_id it check checkin and checkout are
        filled or not if not then raise warning
        -----------------------------------------------------------
        @param self: object pointer
        """
        if not self.line_id.checkin:
            raise ValidationError(
                _(
                    """Alert!, Before choosing a room,\n You have to """
                    """select a Check in date or a Check out """
                    """ date in the reservation form."""
                )
            )
        hotel_room_ids = self.env["hotel.room"].search(
            [("room_categ_id", "=", self.categ_id.id)]
        )
        room_ids = []
        for room in hotel_room_ids:
            assigned = False
            for line in room.room_reservation_line_ids.filtered(
                    lambda l: l.status != "cancel"
            ):
                if self.line_id.checkin and line.check_in and self.line_id.checkout:
                    if (
                            self.line_id.checkin <= line.check_in <= self.line_id.checkout
                    ) or (
                            self.line_id.checkin <= line.check_out <= self.line_id.checkout
                    ):
                        assigned = True
                    elif (line.check_in <= self.line_id.checkin <= line.check_out) or (
                            line.check_in <= self.line_id.checkout <= line.check_out
                    ):
                        assigned = True
            for rm_line in room.room_line_ids.filtered(lambda l: l.status != "cancel"):
                if self.line_id.checkin and rm_line.check_in and self.line_id.checkout:
                    if (
                            self.line_id.checkin
                            <= rm_line.check_in
                            <= self.line_id.checkout
                    ) or (
                            self.line_id.checkin
                            <= rm_line.check_out
                            <= self.line_id.checkout
                    ):
                        assigned = True
                    elif (
                            rm_line.check_in <= self.line_id.checkin <= rm_line.check_out
                    ) or (
                            rm_line.check_in <= self.line_id.checkout <= rm_line.check_out
                    ):
                        assigned = True
            if not assigned:
                room_ids.append(room.id)
        domain = {"reserve": [("id", "in", room_ids)]}
        return {"domain": domain}

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        hotel_room_reserv_line_obj = self.env["hotel.room.reservation.line"]
        for reserv_rec in self:
            for rec in reserv_rec.reserve:
                myobj = hotel_room_reserv_line_obj.search(
                    [
                        ("room_id", "=", rec.id),
                        ("reservation_id", "=", reserv_rec.line_id.id),
                    ]
                )
                if myobj:
                    rec.write({"isroom": True, "status": "available"})
                    myobj.unlink()
        return super(HotelReservationLine, self).unlink()


#
class HotelRoomReservationLine(models.Model):
    _name = "hotel.room.reservation.line"
    _description = "Hotel Room Reservation"
    _rec_name = "room_id"

    room_id = fields.Many2one("hotel.room", string="Room id")
    check_in = fields.Datetime("Check In Date", required=True)
    check_out = fields.Datetime("Check Out Date", required=True)
    state = fields.Selection(
        [("assigned", "Assigned"), ("unassigned", "Unassigned")], "Room Status"
    )
    reservation_id = fields.Many2one("hotel.reservation", "Reservation")
    status = fields.Selection(string="state", related="reservation_id.state")


class HotelBookingSource(models.Model):
    _name = "hotel.booking.source"
    _description = "Hotel Booking Source"

    name = fields.Char(string="Name")


class HotelGuestType(models.Model):
    _name = "hotel.guest.type"
    _description = "Hotel Guest Type"

    name = fields.Char(string="Guest Type")
