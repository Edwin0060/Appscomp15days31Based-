from odoo import api, fields, models, _


class HotelFolio(models.Model):
    _inherit = "hotel.folio"
    _order = "reservation_id desc"

    reservation_id = fields.Many2one(
        "hotel.reservation", "Reservation", ondelete="restrict"
    )
    hotel_house_keeping_orders = fields.One2many(
        "house.keeping.details", 'proforma_id'
    )


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
    internal_room = fields.Char('Internal Room No')
    room_id = fields.Many2one(
        "hotel.reservation",
        "External Room No",
    )
    inspector_id = fields.Many2one(
        "res.users",
        "Inspector",
    )
    inspect_date_time = fields.Datetime(
        "Inspect Date Time",
    )


class HotelButtonBox(models.Model):
    _inherit = "hotel.room"

    user_room_count = fields.Integer(string="House Keeping", compute='get_use_room_count')

    def get_use_room_count(self):
        self.user_room_count = self.env['hotel.housekeeping'].sudo().search_count([
            ('hotel_room_id.name', '=', self.name) , ('floor_id.name', '=', self.floor_id.name)])

    def smart_room_button_count(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('hotel_housekeeping.view_hotel_housekeeping_form')
        tree_view = self.sudo().env.ref('hotel_housekeeping.view_hotel_housekeeping_tree')
        kanban_view = self.sudo().env.ref('hotel_housekeeping.view_hotel_housekeeping_kanban')
        return {
            'name': _('House Keeeping Service'),
            'res_model': 'hotel.housekeeping',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form') , (kanban_view.id, 'kanban')],
            'domain': [('hotel_room_id.name', '=', self.name)],
        }


