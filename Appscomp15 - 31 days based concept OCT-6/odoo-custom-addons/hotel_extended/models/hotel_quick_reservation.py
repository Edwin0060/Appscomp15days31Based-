# See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from datetime import date

import datetime


class CheckInCheckList(models.TransientModel):
    _name = 'checkin.checklist'
    _description = 'Room  CheckList Checklist Line'

    name = fields.Char(string='Name')
    product_id = fields.Many2one('product.product', string='Check List')
    room_no = fields.Many2one('quick.room.reservation', string='Company')
    room_reservation = fields.Many2one('hotel.reservation', string='Reservation')
    qty = fields.Integer(string='Quantity')
    things_selection = fields.Selection([
        ('available', 'Available & Good Condition'),
        ('damage_available', 'Available & Damaged'),
        ('non_available', 'Not Available')],
        string='Status',
    )
    checklist_image = fields.Binary(string='Image')

class QuickRoomReservation(models.TransientModel):
    _name = "quick.room.reservation"
    _description = "Quick Room Reservation"

    checkin_checklist_line = fields.One2many(
        "checkin.checklist", "room_no")

    partner_id = fields.Many2one(
        "res.partner",
        string="Guest"
    )
    check_in = fields.Datetime("Check In")
    check_out = fields.Datetime("Check Out")
    room_id = fields.Many2one(
        "hotel.room",
        string="Room"
    )
    room_category = fields.Many2one(related='room_id.room_categ_id', string='Room Category')
    room_floor_id = fields.Many2one(related='room_id.floor_id', string='Floor')
    room_capacity = fields.Integer(related='room_id.capacity', string='Room Capacity')
    room_no = fields.Char(related='room_id.room_no', string='Room No')
    company_id = fields.Many2one(
        "res.company",
        string="Hotel",
        default=lambda self: self.env.company
    )
    guest_type = fields.Selection(
        [("person", "Individual"),
         ("company", "Company")],
        string="Guest Type",
        default='person'
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist"
    )
    partner_invoice_id = fields.Many2one(
        "res.partner",
        string="Invoice Address"
    )
    partner_order_id = fields.Many2one(
        "res.partner",
        string="Ordering Contact"
    )
    partner_shipping_id = fields.Many2one(
        "res.partner",
        string="Delivery Address"
    )
    room_image = fields.Binary(
        string='Room Image',
        related='room_id.image_1920'
    )
    adults = fields.Integer("Adults")
    children = fields.Integer("Children")
    guest_creation = fields.Selection(
        [("exist", "Exist"),
         ("new", "New")],
        string="Guest Status",
        default='new'
    )
    room_amenities_ids = fields.Many2many(
        "hotel.room.amenities",
        string="Room Amenities",
        help="List of room amenities.",
        related='room_id.room_amenities_ids'
    )
    name = fields.Char(string='Guest Name')
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string='E-mail')
    valid_proof = fields.Many2one(
        "identity.register",
        string="Proof Type"
    )
    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High')],
        string='Priority')
    create_guest = fields.Boolean(
        string='Do You Want to Generate a New Guest...?'
    )

    search_mobile = fields.Char('Mobile', readonly=False, store=True)
    choose_payment_mode = fields.Many2one("payment.mode", string="Payment Mode")
    payment_mode_img = fields.Binary(string='Payment Image', related='choose_payment_mode.payment_mode_img')
    journal = fields.Many2one("account.journal", string="Journal")
    advance_amt = fields.Float(string="Advance Payment")
    add_proof_type = fields.Many2one("identity.register", string="Proof Type")
    add_proof = fields.Binary(string='Proof')

    active = fields.Boolean('Active', tracking=True)
    reserve_date = fields.Date(string="Date")
    check_in_time = fields.Char(string="Check In Time")
    check_out_time = fields.Char(string="Check Out Time")
    room_price = fields.Float(related='room_id.list_price', string="Price")
    hrs_selection = fields.Selection([
        ('short', 'Free Hours'),
        ('12', '12 Hours'),
        ('24', '24 Hours'), ],
        string='Hours',
    )
    manuly_enter_hrs = fields.Integer(string="Time")
    company_currency = fields.Many2one(related='company_id.currency_id', string="Currency", )

    summary_header = fields.Text("Summary Header")
    room_summary = fields.Text("Room Summary")
    date_today = fields.Date("Date", default=lambda self: fields.Date.today())
    time_interval = fields.Char('Time Interval')
    remaining_time = fields.Char(string="Remaining Time", compute="_compute_remain_hrs")
    guest_type_nation = fields.Many2one('hotel.guest.type', string='Guest Type')
    booking_source = fields.Many2one('hotel.booking.source', string='Booking Source')

    amount_Receive = fields.Char('Amount state')

    @api.onchange('mobile')
    def mobile_already_exits_function(self):
        if self.mobile:
            if len(self.mobile) > 9:
                search = self.env['res.partner'].search([('mobile', '=', self.mobile)])
                if search:
                    raise ValidationError(_(' Alert!!.. Mobile Number Already Exits'))
                else:
                    pass


    @api.onchange('room_id')
    def fetch_data_checklistline(self):
        room_obj = self.env["hotel.room"]
        room_ids = room_obj.search([('name', '=', self.room_id.name)])
        list = [(5, 0, 0)]
        for i in room_ids.cheack_line_ids:
            vals = {
                'product_id': i.product_id.id,
                'things_selection': i.things_selection,
                'qty': i.qty,
                'checklist_image': i.checklist_image
            }
            list.append((0, 0, vals))
        self.checkin_checklist_line = list

    """ 
    Onchange function for Selected Room Category the price has been 
    updated based on Selected price-list 
    """
    @api.onchange('pricelist_id', 'room_price')
    def room_price_list(self):
        if self.pricelist_id:
            price_info_id = self.env['product.pricelist'].sudo().search([('id', '=', self.pricelist_id.id)])
            if self.pricelist_id:
                for price_list in price_info_id.item_ids:
                    if price_list.product_tmpl_id.name == self.room_id.name:
                        self.room_price = price_list.fixed_price

    @api.depends('remaining_time', 'guest_creation')
    def _compute_remain_hrs(self):
        ConvertedSec = 86400.0
        room_obj = self.env["hotel.room"].search([('room_no', '=', self.room_no)])
        if room_obj.room_reservation_line_ids:
            for reserve_val in room_obj.room_reservation_line_ids:
                print(ConvertedSec)
                reserve_checkin = reserve_val.check_in + timedelta(hours=5, minutes=30)
                reserve_checkout = reserve_val.check_out + timedelta(hours=5, minutes=30)
                cit = reserve_checkin.date()
                cot = reserve_checkout.date()
                if cit <= self.date_today <= cot:
                    import datetime
                    if self.date_today == cot and self.date_today != cit:
                        time = str(reserve_checkout.time())
                        date_time = datetime.datetime.strptime(time, "%H:%M:%S")
                        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
                        seconds = a_timedelta.total_seconds()
                        ConvertedSec = ConvertedSec - seconds
                        day_full_time = str(datetime.timedelta(seconds=ConvertedSec))
                        self.remaining_time = day_full_time
                    elif self.date_today == cit and self.date_today != cot:
                        time = str(reserve_checkin.time())
                        date_time = datetime.datetime.strptime(time, "%H:%M:%S")
                        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
                        seconds = a_timedelta.total_seconds()
                        row_seconds = 86400.0 - seconds
                        ConvertedSec = ConvertedSec - row_seconds
                        day_full_time = str(datetime.timedelta(seconds=ConvertedSec))
                        self.remaining_time = day_full_time
                        print(seconds, "===========", ConvertedSec, "+====", time, "===========", day_full_time,
                              "========")
                    elif self.date_today == cit and self.date_today == cot:
                        print("==========================Gokul")
                        time = str(reserve_val.check_out - reserve_val.check_in)
                        date_time = datetime.datetime.strptime(time, "%H:%M:%S")
                        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
                        seconds = a_timedelta.total_seconds()
                        ConvertedSec = ConvertedSec - seconds
                        day_full_time = str(datetime.timedelta(seconds=ConvertedSec))
                        self.remaining_time = day_full_time
                        print(seconds, "===========", time, "===========", day_full_time, "========")

                else:
                    self.remaining_time = "24:00:00"
        else:
            self.remaining_time = "24:00:00"

    @api.onchange('choose_payment_mode')
    def change_journal(self):
        journal = self.env['account.journal'].sudo().search([
            ('name', '=', self.choose_payment_mode.name)])
        for rec in journal:
            print('+++++++++', rec.name)
            self.update({
                'journal': journal
            })
        self.company_currency = self.env.company.currency_id

    @api.onchange('adults', 'children')
    def capacity_validation(self):
        total = self.children + self.adults
        if int(self.room_capacity) == int(total):
            pass
        if int(self.room_capacity) < int(total):
            raise ValidationError(_(' Alert!!.. Room Capacity is Greater then Adults & children'))

    @api.onchange('hrs_selection')
    def calculate_hours(self):
        if self.hrs_selection == str(12):
            time = str(self.check_in)
            datetime_object = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            cot = datetime_object + timedelta(hours=12, minutes=00)
            self.check_out = cot
        elif self.hrs_selection == str(24):
            time = str(self.check_in)
            datetime_object = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            cot = datetime_object + timedelta(hours=24, minutes=00)
            self.check_out = cot

    @api.onchange('manuly_enter_hrs')
    def manuly_enter_hours(self):
        if self.hrs_selection == 'short':
            time = str(self.check_in)
            datetime_object = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            cot = datetime_object + timedelta(hours=self.manuly_enter_hrs, minutes=00)
            self.check_out = cot

    @api.onchange('check_in', 'check_out')
    def validation_reserve(self):
        room_obj = self.env["hotel.room"].search([('room_no', '=', self.room_no)])
        if self.check_out:
            for i in room_obj.room_reservation_line_ids:
                if i.check_in < self.check_in < i.check_out:
                    raise ValidationError(_('Alert!!.. Already Room Is Booking In Your Check In Time'))
                elif i.check_in < self.check_out < i.check_out:
                    raise ValidationError(_('Alert!!.. Already Room Is Booking In Your Check Out Time'))
                elif self.check_in < i.check_in < self.check_out:
                    raise ValidationError(_('Alert!!.. Already Room Is Booking In Your Check In Time'))

    @api.onchange('search_mobile')
    def _compute_mobile(self):
        if self.search_mobile:
            mobile = self.env['res.partner'].sudo().search([
                ('mobile', '=', self.search_mobile)])
            self.write({
                'partner_id': mobile.id
            })
            print("============================11111111111111",date.today())
        else:
            self.write({
                'partner_id': False
            })

    @api.onchange("check_out", "check_in")
    def _on_change_check_out(self):
        """
        When you change checkout or checkin it will check whether
        Checkout date should be greater than Checkin date
        and update dummy field
        -----------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        if (self.check_out and self.check_in) and (self.check_out < self.check_in):
            raise ValidationError(
                _("Checkout date should be greater than Checkin date.")
            )

    @api.onchange("partner_id")
    def _onchange_partner_id_res(self):
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

    @api.onchange('search_mobile')
    def onchange_proof(self):
        if self.search_mobile:

            details = self.env['res.partner'].sudo().search([
                ('mobile', '=', self.search_mobile)])
            self.write({
                "add_proof_type": details.proof_type.id
            })

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        res = super(QuickRoomReservation, self).default_get(fields)
        keys = self._context.keys()
        # print("===============================", keys, "==================", self._context.values())
        if "date" in keys:
            res.update({"reserve_date": self._context["date"]})
        if "box_date" in keys:
            res.update({"date_today": self._context["box_date"]})
        if "entry" in keys:
            res.update({"check_in_time": self._context["entry"]})
        if "date" in keys:
            if str(date.today()) == str(self._context["date"]).split(" ")[0]:
                now = str(datetime.datetime.now()).split(".")[0]
                current_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
            else:
                time = self._context["date"]
                datetime_object = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                current_time = datetime_object - timedelta(hours=5, minutes=30)
            res.update({"check_in": current_time})
        if "room_id" in keys:
            roomid = self._context["room_id"]
            res.update({"room_id": int(roomid)})
        return res

    def room_reserve(self):

        """
        This method create a new record for hotel.reservation
        -----------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel reservation.
        """
        global datetime_object_2
        hotel_advance_pay = self.env["account.payment"]
        hotel_res_obj = self.env["hotel.reservation"]
        for i in self:
            rec = hotel_advance_pay.create(
                {
                    "partner_id": i.partner_id.id,
                    "amount": i.advance_amt,
                    "journal_id": i.journal.id,
                }
            )
        res_partner = self.env['res.partner'].sudo().search([
            ('name', '=', self.partner_id.name)])
        res_partner.write({
            'proof_img': self.add_proof,
        })
        journal = self.env["account.payment"].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('amount', '=', self.advance_amt),
            ('date', '=', date.today()),
            ('journal_id', '=', self.journal.id),
        ])
        print("=====================", journal)
        journal.action_post()
        print("==========================",journal.state)
        if journal.state == 'posted':
            self.amount_Receive = 'Received'
        elif journal.state == 'draft':
            self.amount_Receive = 'Progress'

        if self.check_in and self.check_out:
            for res in self:
                if self.advance_amt == 0:
                    print('*************ZERO******************')
                    rec = hotel_res_obj.create(
                        {
                            "partner_id": res.partner_id.id,
                            "partner_invoice_id": res.partner_invoice_id.id,
                            "partner_order_id": res.partner_order_id.id,
                            "partner_shipping_id": res.partner_shipping_id.id,
                            "checkin": res.check_in,
                            "checkout": res.check_out,
                            "reservation_hrs_selection": res.hrs_selection,
                            "company_id": res.company_id.id,
                            "pricelist_id": res.pricelist_id.id,
                            "adults": res.adults,
                            "children": res.children,
                            "proof_type": res.add_proof,
                            "guest_type_nation": res.guest_type_nation.id,
                            "booking_source": res.booking_source.id,
                            "amount_Receive": res.amount_Receive,
                            "advance_payment": res.advance_amt,
                            "reservation_line": [
                                (
                                    0,
                                    0,
                                    {
                                        "reserve": [(6, 0, res.room_id.ids)],
                                        "name": res.room_id.name or " ",
                                    },
                                )
                            ],
                        }

                    )
                else:
                    print('************* NON ZERO******************')
                    hotel_res_obj.create({
                        "partner_id": res.partner_id.id,
                        "partner_invoice_id": res.partner_invoice_id.id,
                        "partner_order_id": res.partner_order_id.id,
                        "partner_shipping_id": res.partner_shipping_id.id,
                        "checkin": res.check_in,
                        "checkout": res.check_out,
                        "reservation_hrs_selection": res.hrs_selection,
                        "company_id": res.company_id.id,
                        "pricelist_id": res.pricelist_id.id,
                        "adults": res.adults,
                        "children": res.children,
                        "proof_type": res.add_proof,
                        "guest_type_nation": res.guest_type_nation.id,
                        "booking_source": res.booking_source.id,
                        "amount_Receive": res.amount_Receive,
                        "state": "confirm",
                        "advance_payment": res.advance_amt,
                        "reservation_line": [
                            (
                                0,
                                0,
                                {
                                    "reserve": [(6, 0, res.room_id.ids)],
                                    "name": res.room_id.name or " ",
                                },
                            )
                        ],
                    })
                    hotel_res_obj_new = self.env["hotel.reservation"].search([
                        ("partner_id", "=", res.partner_id.id),
                        ("checkin", "=", res.check_in),
                        ("checkout", "=", res.check_out),
                        ("adults", "=", res.adults),
                        # ("reservation_line.name", "=", res.room_id.name),
                    ])
                    list = [(5, 0, 0)]
                    for i in self.checkin_checklist_line:
                        values = {
                            'product_id': i.product_id.id,
                            'things_selection': i.things_selection,
                            'qty': i.qty,
                            'checklist_image': i.checklist_image
                        }
                        list.append((0, 0, values))
                    hotel_res_obj_new.checkin_checklist_line = list
                    vals = {
                        "room_id": res.room_id.id,
                        "check_in": res.check_in,
                        "check_out": res.check_out,
                        "state": "assigned",
                        "status": "confirm",
                        "reservation_id": hotel_res_obj_new.id,
                    }
                    self.room_id.room_reservation_line_ids.sudo().create(vals)
            folio = hotel_res_obj.sudo().search([
                        ("partner_id", "=", self.partner_id.id),
                        ("checkin", "=", self.check_in),
                        ("checkout", "=", self.check_out),
                        ("adults", "=", self.adults),
            ])
            folio.create_folio()
        return rec

    @api.onchange('create_guest')
    def create_new_guest(self):
        for val in self:
            if val.name and val.create_guest:
                values = {
                    'name': val.name,
                    'email': val.email,
                    'mobile': val.mobile,
                    'company_type': val.guest_type,
                    'proof_type': val.valid_proof.id,
                }
                self.env['res.partner'].sudo().create(values)
                partner = self.env['res.partner'].sudo().search([
                    ('name', '=', self.name)])
                self.write({
                    'guest_creation': 'exist',
                    'partner_id': partner.id,
                    'search_mobile': val.mobile,
                })

    """
    This is a comment
    written in
    Time based widget per day based room
    """

    def room_reservation(self):
        """room_line_ids
        @param self: object pointer
        """
        resource_id = self.env.ref("hotel_extended.view_hotel_reservation_form").id
        return {
            "name": _("Reconcile Write-Off"),
            "context": self._context,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "hotel.reservation",
            "views": [(resource_id, "form")],
            "type": "ir.actions.act_window",
            "target": "new",
        }

    @api.onchange("date_today", "time_interval")
    def get_room_summary_for_day_in_one_room(self):
        import datetime
        start = "00:00"
        end = "23:59"
        if self.time_interval:
            delta = datetime.timedelta(minutes=int(self.time_interval))
        start = datetime.datetime.strptime(start, '%H:%M')
        end = datetime.datetime.strptime(end, '%H:%M')
        t = start
        summary_header_list = []
        if self.time_interval:
            while t <= end:
                interval = datetime.datetime.strftime(t, '%H:%M')
                summary_header_list.append(interval)
                t += delta
        global reserve_checkin_date, reserve_checkout_date
        hours = [(n, "%d %s" % (n % 12 or 12, ["AM", "PM"][n > 11])) for n in range(24)]
        res = {}
        all_detail = []
        main_header = []
        all_room_detail = []
        # domain = [('check_in', '=', self.date_today), ('check_out', '=', self.date_today)]
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        room_obj = self.env["hotel.room"]
        room_num_ids = set()
        domain = [('room_no', '=', self.room_no)]
        box_date = self.date_today
        if not self.time_interval:
            for time in hours:
                summary_header_list.append(time[1])
            room_ids = room_obj.search(domain)
            print("================", room_ids)
            for room in room_ids:
                print("************************")
                room_detail = {}
                room_list_stats = []
                chk_date = self.date_today
                room_detail.update({"name": room.name or ""})
                if room.room_reservation_line_ids:
                    for entry in summary_header_list:
                        m2 = datetime.datetime.strptime(entry, '%I %p')
                        m3 = str(m2).split(':')[0].split(' ')[-1]
                        room_list_stats.append(
                            {
                                "state": "Free",
                                "date": str(chk_date),
                                "room_id": room.id,
                                "entry": m3 + ':' + '00',
                            }
                        )
                    for reserve_val in room.room_reservation_line_ids:
                        reserve_checkin = reserve_val.check_in + timedelta(hours=5, minutes=30)
                        reserve_checkout = reserve_val.check_out + timedelta(hours=5, minutes=30)
                        reserve_checkin_date = reserve_checkin.date()
                        reserve_checkin_time = reserve_checkin.time()
                        reserve_checkout_date = reserve_checkout.date()
                        reserve_checkout_time = reserve_checkout.time()
                        if room.id not in room_num_ids:
                            print("==========",reserve_val)
                            room_num_ids.add(room.id)
                            if reserve_checkin_date <= chk_date <= reserve_checkout_date:
                                print("===================_______++++++++++++++++")
                                # Equal to checkout date
                                if chk_date == reserve_checkin_date and chk_date == reserve_checkin_date:
                                    checkin_time = str(reserve_checkin_time).split(':')[0]
                                    checkout_time = str(reserve_checkout_time).split(':')[0]
                                    for i in room_list_stats:
                                        if i['state'] == 'Free' and str(i['date']) == str(chk_date) and \
                                                checkout_time + ':' + '00' >= i['entry'] >= checkin_time + ':' + '00':
                                            i.update(
                                                {
                                                    "state": "Reserved",
                                                    "date": str(chk_date),
                                                    "room_id": room.id,
                                                    "floor_id": room.floor_id.id,
                                                    "is_draft": "No",
                                                    "data_model": "",
                                                    "data_id": reserve_val.reservation_id.id or 0,
                                                })

                                if chk_date == reserve_checkout_date and chk_date != reserve_checkin_date:
                                    chk_out_time = str(reserve_checkin_time).split(':')[0]
                                    for i in room_list_stats:
                                        if i['state'] == 'Free' and str(i['date']) == str(chk_date) and \
                                                i['entry'] <= chk_out_time + ':' + '00':
                                            i.update(
                                                {
                                                    "state": "Reserved",
                                                    "date": str(chk_date),
                                                    "room_id": room.id,
                                                    "floor_id": room.floor_id.id,
                                                    "is_draft": "No",
                                                    "data_model": "",
                                                    "data_id": reserve_val.reservation_id.id or 0,
                                                }
                                            )
                                elif chk_date != reserve_checkin_date and chk_date != reserve_checkout_date:
                                    for i in room_list_stats:
                                        if i['state'] == 'Free' and str(i['date']) == str(chk_date):
                                            i.update(
                                                {
                                                    "state": "Reserved",
                                                    "date": str(chk_date),
                                                    "room_id": room.id,
                                                    "floor_id": room.floor_id.id,
                                                    "is_draft": "No",
                                                    "data_model": "",
                                                    "data_id": reserve_val.reservation_id.id or 0,
                                                }
                                            )

                                # Equal to checkin date
                                elif chk_date == reserve_checkin_date and chk_date != reserve_checkout_date:
                                    chk_in_time = str(reserve_checkin_time).split(':')[0]
                                    for i in room_list_stats:
                                        if i['state'] == 'Free' and str(i['date']) == str(chk_date) and \
                                                i['entry'] >= chk_in_time + ':' + '00':
                                            i.update(
                                                {
                                                    "state": "Reserved",
                                                    "date": str(chk_date),
                                                    "room_id": room.id,
                                                    "floor_id": room.floor_id.id,
                                                    "is_draft": "No",
                                                    "data_model": "",
                                                    "data_id": reserve_val.reservation_id.id or 0,
                                                }
                                            )

                        else:
                            print(reserve_val.check_out)
                            if reserve_checkin_date <= chk_date <= reserve_checkout_date:
                                print("===================_______++++++++++++++++")
                                # Equal to checkout date
                                if chk_date == reserve_checkin_date and chk_date == reserve_checkin_date:
                                    checkin_time = str(reserve_checkin_time).split(':')[0]
                                    checkout_time = str(reserve_checkout_time).split(':')[0]
                                    for i in room_list_stats:
                                        if i['state'] == 'Free' and str(i['date']) == str(chk_date) and \
                                                checkout_time + ':' + '00' >= i['entry'] >= checkin_time + ':' + '00':
                                            i.update(
                                                {
                                                    "state": "Reserved",
                                                    "date": str(chk_date),
                                                    "room_id": room.id,
                                                    "floor_id": room.floor_id.id,
                                                    "is_draft": "No",
                                                    "data_model": "",
                                                    "data_id": reserve_val.reservation_id.id or 0,
                                                })

                                if chk_date == reserve_checkout_date and chk_date != reserve_checkin_date:
                                    chk_out_time = str(reserve_checkout_time).split(':')[0]
                                    for i in room_list_stats:
                                        if i['state'] == 'Free' and str(i['date']) == str(chk_date) and \
                                                i['entry'] < chk_out_time + ':' + '00':
                                            i.update(
                                                {
                                                    "state": "Reserved",
                                                    "date": str(chk_date),
                                                    "room_id": room.id,
                                                    "floor_id": room.floor_id.id,
                                                    "is_draft": "No",
                                                    "data_model": "",
                                                    "data_id": reserve_val.reservation_id.id or 0,
                                                }
                                            )
                                elif chk_date != reserve_checkin_date and chk_date != reserve_checkout_date:
                                    for i in room_list_stats:
                                        if i['state'] == 'Free' and str(i['date']) == str(chk_date):
                                            i.update(
                                                {
                                                    "state": "Reserved",
                                                    "date": str(chk_date),
                                                    "room_id": room.id,
                                                    "floor_id": room.floor_id.id,
                                                    "is_draft": "No",
                                                    "data_model": "",
                                                    "data_id": reserve_val.reservation_id.id or 0,
                                                }
                                            )

                                # Equal to checkin date
                                elif chk_date == reserve_checkin_date and chk_date != reserve_checkout_date:
                                    chk_in_time = str(reserve_checkin_time).split(':')[0]
                                    for i in room_list_stats:
                                        if i['state'] == 'Free' and str(i['date']) == str(chk_date) and \
                                                i['entry'] >= chk_in_time + ':' + '00':
                                            i.update(
                                                {
                                                    "state": "Reserved",
                                                    "date": str(chk_date),
                                                    "room_id": room.id,
                                                    "floor_id": room.floor_id.id,
                                                    "is_draft": "No",
                                                    "data_model": "",
                                                    "data_id": reserve_val.reservation_id.id or 0,
                                                }
                                            )


                else:
                    for entry in summary_header_list:
                        m2 = datetime.datetime.strptime(entry, '%I %p')
                        m3 = str(m2).split(':')[0].split(' ')[-1]
                        room_list_stats.append(
                            {
                                "state": "Free",
                                "date": str(chk_date),
                                "room_id": room.id,
                                "entry": m3 + ':' + '00',
                            }
                        )

                room_detail.update({"value": room_list_stats})
                all_room_detail.append(room_detail)

        summary_header_list.insert(0, "Rooms")
        main_header.append({"header": summary_header_list})

        self.summary_header = str(main_header)
        self.room_summary = str(all_room_detail)

        return res
