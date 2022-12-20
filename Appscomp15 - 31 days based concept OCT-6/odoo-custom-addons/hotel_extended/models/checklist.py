from odoo import api, fields, models, _


class HousekeepingChecklistLine(models.Model):
    _name = 'housekeeping.checklist.line'
    _description = 'House Keeping Checklist Line'

    name = fields.Char(string='Name')
    room_id = fields.Many2one('hotel.folio', string='Company')
    product_id = fields.Many2one('product.product', string='Check List')
    true = fields.Boolean('True')
    false = fields.Boolean('False')
    remarks = fields.Char(string='Remarks')
    qty = fields.Integer(string='Quantity')
    things_selection = fields.Selection([
        ('available', 'Available & Good Condition'),
        ('damage_available', 'Available & Damaged'),
        ('non_available', 'Not Available')],
        string=' Check IN Status',
    )
    Checkout_things_selection = fields.Selection([
        ('available', 'Available & Good Condition'),
        ('damage_available', 'Available & Damaged'),
        ('non_available', 'Not Available')],
        string=' Check Out Status',
    )
    reservation_checklist_image = fields.Binary(string='Image')

    def click_yes(self):
        self.write({
            'Checkout_things_selection': 'available', })
        room_obj = self.env["hotel.room"].search([('name', '=', self.room_id.ref_name.name)])
        print("=============", room_obj.name)
        for room in room_obj.cheack_line_ids:
            if self.product_id.name == room.product_id.name:
                print("=====11111111111========", room_obj)
                room.write({
                    'things_selection': 'available'
                })

    def click_no(self):
        self.write({
            'Checkout_things_selection': 'non_available', })
        room_obj = self.env["hotel.room"].search([('name', '=', self.room_id.ref_name.name)])
        for room in room_obj.cheack_line_ids:
            if self.product_id.name == room.product_id.name:
                room.write({
                    'things_selection': 'non_available'
                })

    def click_damaged(self):
        self.write({
            'Checkout_things_selection': 'damage_available', })
        room_obj = self.env["hotel.room"].search([('name', '=', self.room_id.ref_name.name)])
        for room in room_obj.cheack_line_ids:
            if self.product_id.name == room.product_id.name:
                room.write({
                    'things_selection': 'damage_available'
                })


class RoomChecklistLine(models.Model):
    _name = 'room.checklist.line'
    _description = 'Room Checklist Line'

    name = fields.Char(string='Name')
    product_id = fields.Many2one('product.product', string='Check List')
    room_no = fields.Many2one('hotel.room', string='Company')
    remarks = fields.Char(string='Remarks')
    qty = fields.Integer(string='Quantity')
    things_selection = fields.Selection([
        ('available', 'Available & Good Condition'),
        ('damage_available', 'Available & Damaged'),
        ('non_available', 'Not Available')],
        string='Status',
    )
    checklist_image = fields.Binary(string='Image', related='product_id.image_1920')


class HousekepingChecklist(models.Model):
    _inherit = 'hotel.folio'
    _description = 'House Folio '

    ref_no = fields.Many2one("hotel.reservation", "Reservation ID")
    ref_name = fields.Many2one("hotel.room", "Room Name")

    cheacklist_line_ids = fields.One2many(
        "housekeeping.checklist.line", "room_id")

    @api.onchange('ref_name')
    def fetch_checklist(self):
        room_obj = self.env["hotel.reservation"]
        room_ids = room_obj.search([('reservation_no', '=', self.reservation_id.reservation_no)])
        list = [(5, 0, 0)]
        for i in room_ids.checkin_checklist_line:
            vals = {
                'product_id': i.product_id.id,
                'things_selection': i.things_selection,
                'qty': i.qty,
                'reservation_checklist_image': i.checklist_image
            }
            list.append((0, 0, vals))
        self.cheacklist_line_ids = list


class Checklist(models.Model):
    _inherit = 'hotel.room'
    _description = 'Hotel Room Check List'

    cheack_line_ids = fields.One2many(
        "room.checklist.line", "room_no")
