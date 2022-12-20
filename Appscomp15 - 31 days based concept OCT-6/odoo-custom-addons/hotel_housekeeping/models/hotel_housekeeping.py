# See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HotelHousekeeping(models.Model):
    _name = "hotel.housekeeping"
    _description = "Hotel Housekeeping"
    _rec_name = "room_id"

    # def name_get(self):
    #     self.hotel_rooms = []
    #     for rec in self:
    #         name = rec.hotel_room_id.name
    #         roomno = rec.hotel_room_id.room_no
    #         rec.hotel_rooms.append((roomno, name))
    #     return rec.hotel_rooms
    name = fields.Char(string="Name", default="/", readonly=True)
    current_date = fields.Date(
        "Today's Date",
        required=True,
        index=True,
        states={"done": [("readonly", True)]},
        default=fields.Date.today,
    )

    clean_type = fields.Selection(
        [
            ("daily", "Daily"),
            ("checkin", "Check-In"),
            ("checkout", "Check-Out"),
        ],
        "Clean Type",
        required=True,
        states={"done": [("readonly", True)]},
    )
    activity_type = fields.Selection(
        [
            ("internal", "Internal Activity "),
            ("external", " External Activity"),
        ],
        "Activity Type", default='external',
        required=True)
    room_id = fields.Many2one("hotel.reservation", "Reservation ID")
    hotel_room_id = fields.Many2one("hotel.room", "Reservation ID")
    floor_id = fields.Many2one("hotel.floor", "Floor ")
    hotel_rooms = fields.Char("Rooms Details")
    categ = fields.Many2one("hotel.room.type", "Room")
    room_number = fields.Char("Room No")
    room_num_in_squ = fields.Char("Number")

    activity_line_ids = fields.One2many(
        "hotel.housekeeping.activities",
        "housekeeping_id",
        "Activities",
        states={"done": [("readonly", True)]},
        help="Detail of housekeeping \
                                        activities",
    )
    inspector_id = fields.Many2one(
        "res.users",
        "Inspector",
        required=True,
        states={"done": [("readonly", True)]},
    )
    inspect_date_time = fields.Datetime(
        "Inspect Date Time",
        required=True,
        states={"done": [("readonly", True)]},
    )
    quality = fields.Selection(
        [
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("average", "Average"),
            ("bad", "Bad"),
            ("ok", "Ok"),
        ],
        "Quality",
        states={"done": [("readonly", True)]},
        help="Inspector inspect the room and mark \
                                as Excellent, Average, Bad, Good or Ok. ",
    )
    state = fields.Selection(
        [
            ("inspect", "Inspect"),
            ("dirty", "Dirty"),
            ("clean", "Clean"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        "State",
        states={"done": [("readonly", True)]},
        required=True,
        readonly=True,
        default="inspect",
    )

    housekeeping_cancel_remarks = fields.Text(string='Housekeeping Cancel Remarks')
    housekeeping_cancel_remarks_2 = fields.Text(string='Housekeeping Cancel Remarks')
    housekeeping_cancel_remarks_3 = fields.Text(string='Housekeeping Cancel Remarks')

    @api.onchange('floor_id', 'categ', 'room_number')
    def onchange_room_number(self):
        floor = self.floor_id.short_code
        category = self.categ.short_code
        if floor and category and self.room_number:
            self.room_num_in_squ = str(floor) + '/' + str(category) + '/' + str(self.room_number)

    def house_keeping_cancel(self):
        view_id = self.env['housekeeping.cancel']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hotel Management Table Order Cancel Remarks',
            'res_model': 'housekeeping.cancel',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('hotel_housekeeping.hotel_management_table_cancel_remarks_wizard', False).id,
            'target': 'new',
        }

    def action_set_to_dirty(self):
        """
        This method is used to change the state
        to dirty of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "dirty", "quality": False})
        self.activity_line_ids.write({"is_clean": False, "is_dirty": True})

    def room_cancel(self):
        """
        This method is used to change the state
        to cancel of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "cancel", "quality": False})

    def get_service_order_line_items(self):
        line_vals = []
        for line in self.activity_line_ids:
            if self.activity_line_ids:
                vals = [0, 0, {
                    'product_id': line.activity_id.id,
                    'product_uom_qty': len(self.activity_line_ids),
                    'name': line.housekeeper_id.name,

                }]
                line_vals.append(vals)
        return line_vals

    def proforma_housekeeping_activity(self):
        if self.activity_type == 'external':
            line_vals = []

            vals = [0, 0, {
                'current_date': self.current_date,
                'clean_type': self.clean_type,
                'room_id': self.room_id.id,
                'inspector_id': self.inspector_id.id,
                'inspect_date_time': self.inspect_date_time,
            }]
            line_vals.append(vals)
            return line_vals

        if self.activity_type == 'internal':
            line_vals = []

            vals = [0, 0, {
                'current_date': self.current_date,
                'clean_type': self.clean_type,
                'internal_room': self.room_num_in_squ,
                'inspector_id': self.inspector_id.id,
                'inspect_date_time': self.inspect_date_time,
            }]
            line_vals.append(vals)
            return line_vals

        

    def room_done(self):
        """
        This method is used to change the state
        to done of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        if self.room_id:
            folio_id = self.env['hotel.folio'].sudo().search([('reservation_id', '=', self.room_id.id)])
        else:
            folio_id = self.env['hotel.folio'].sudo().search([("room_num_floor", "=", self.room_num_in_squ)])

        folio_id.sudo().write({
            'hotel_house_keeping_orders': self.proforma_housekeeping_activity(),
            'service_line_ids': self.get_service_order_line_items(),
        })
        if not self.quality:
            raise ValidationError(_("Alert!, Please update quality of work!"))

        # else:
        #     raise ValidationError(_("Alert!, Please Create a Folio against the Reservation"))
        self.write({"state": "done"})

    def room_inspect(self):
        """
        This method is used to change the state
        to inspect of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "inspect", "quality": False})

    def room_clean(self):
        """
        This method is used to change the state
        to clean of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "clean", "quality": False})
        self.activity_line_ids.write({"is_clean": True, "is_dirty": False})

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            if vals.get('activity_type') == 'internal':
                vals['name'] = self.env['ir.sequence'].next_by_code('hotel.internal.housekeeping') or '/'
            if vals.get('activity_type') == 'external':
                vals['name'] = self.env['ir.sequence'].next_by_code('hotel.external.housekeeping') or '/'

        return super(HotelHousekeeping, self).create(vals)
