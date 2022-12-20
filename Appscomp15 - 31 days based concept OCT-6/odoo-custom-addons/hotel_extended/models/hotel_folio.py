# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HotelFolio(models.Model):

    _inherit = "hotel.folio"
    _order = "reservation_id desc"

    reservation_id = fields.Many2one(
        "hotel.reservation", "Reservation", ondelete="restrict"
    )
    room_num_floor = fields.Char("Room Number" ,compute='get_room_num_floor')

    @api.depends('reservation_id')
    def get_room_num_floor(self):
        room = self.env['hotel.room'].sudo().search([
            ('name', '=', self.room_line_ids.product_id.name)])
        self.room_num_floor=room.room_no
    def write(self, vals):
        res = super(HotelFolio, self).write(vals)
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        for folio in self:
            reservations = reservation_line_obj.search(
                [("reservation_id", "=", folio.reservation_id.id)]
            )
            if len(reservations) == 1:
                for line in folio.reservation_id.reservation_line:
                    for room in line.reserve:
                        vals = {
                            "room_id": room.id,
                            "check_in": folio.checkin_date,
                            "check_out": folio.checkout_date,
                            "state": "assigned",
                            "reservation_id": folio.reservation_id.id,
                        }
                        reservations.write(vals)
        return res


class HotelFolioLine(models.Model):

    _inherit = "hotel.folio.line"

    @api.onchange("checkin_date", "checkout_date")
    def _onchange_checkin_checkout_dates(self):
        res = super(HotelFolioLine, self)._onchange_checkin_checkout_dates()
        avail_prod_ids = []
        for room in self.env["hotel.room"].search([]):
            assigned = False
            for line in room.room_reservation_line_ids.filtered(
                lambda l: l.status != "cancel"
            ):
                if self.checkin_date and line.check_in and self.checkout_date:
                    if (self.checkin_date <= line.check_in <= self.checkout_date) or (
                        self.checkin_date <= line.check_out <= self.checkout_date
                    ):
                        assigned = True
                    elif (line.check_in <= self.checkin_date <= line.check_out) or (
                        line.check_in <= self.checkout_date <= line.check_out
                    ):
                        assigned = True
            if not assigned:
                avail_prod_ids.append(room.product_id.id)
        return res

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        Update Hotel Room Reservation line history"""
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        room_obj = self.env["hotel.room"]
        prod_id = vals.get("product_id") or self.product_id.id
        checkin = vals.get("checkin_date") or self.checkin_date
        checkout = vals.get("checkout_date") or self.checkout_date

        is_reserved = self.is_reserved
        if prod_id and is_reserved:
            prod_room = room_obj.search([("product_id", "=", prod_id)], limit=1)
            if self.product_id and self.checkin_date and self.checkout_date:
                old_prod_room = room_obj.search(
                    [("product_id", "=", self.product_id.id)], limit=1
                )
                if prod_room and old_prod_room:
                    # Check for existing room lines.
                    rm_lines = reservation_line_obj.search(
                        [
                            ("room_id", "=", old_prod_room.id),
                            ("check_in", "=", self.checkin_date),
                            ("check_out", "=", self.checkout_date),
                        ]
                    )
                    if rm_lines:
                        rm_line_vals = {
                            "room_id": prod_room.id,
                            "check_in": checkin,
                            "check_out": checkout,
                        }
                        rm_lines.write(rm_line_vals)
        return super(HotelFolioLine, self).write(vals)




class HouseKeepingDetails(models.Model):
    _name = 'house.keeping.details'
    _description = 'House Keeping Details'

    proforma_id = fields.Many2one('hotel.folio')
    current_date = fields.Date('Date')
    clean_type = fields.Selection(
        [
            ("daily", "Daily"),
            ("checkin", "Check-In"),
            ("checkout", "Check-Out"),
        ],
        "Clean Type",
    )
    # room_id = fields.Many2one(
    #     "hotel.room",
    #     "Room No",
    # )
    room_id = fields.Many2one(
        "hotel.reservation",
        "Room No",
    )
    inspector_id = fields.Many2one(
        "res.users",
        "Inspector",
    )
    inspect_date_time = fields.Datetime(
        "Inspect Date Time",
    )


class LaundryDetails(models.Model):
    _name = 'laundry.details'
    _description = 'Laundry Details'

    proforma_id = fields.Many2one('hotel.folio')
    name = fields.Char(string="Label", copy=False)
    partner_id = fields.Many2one('res.partner', string='Guest')
    order_date = fields.Datetime(string="Date")
    laundry_person = fields.Many2one('res.users', string='Laundry Person')
    total_amount = fields.Float(string='Total')
