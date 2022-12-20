# See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class HotelFolio(models.Model):

    _inherit = "hotel.folio"

    hotel_reservation_orders_ids = fields.Many2many(
        "hotel.reservation.order",
        "hotel_res_rel",
        "hotel_folio_id",
        "reste_id",
        "Reservation Orders",
    )
    hotel_restaurant_orders_ids = fields.Many2many(
        "hotel.restaurant.order",
        "hotel_res_resv",
        "hfolio_id",
        "reserves_id",
        "Restaurant Orders",
    )
    hotel_bar_orders_ids = fields.Many2many(
        "hotel.bar.order",
        "hotel_res_bar",
        "hotel_bar_folio_id",
        "restbar_id",
        "Bar Orders",
    )
