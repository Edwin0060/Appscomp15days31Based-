from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class HospitalWard(models.Model):
    _name = "hospital.ward"
    _description = "Hospital Ward"
    _order = "sequence"

    name = fields.Char("Ward Name", required=True, index=True)
    sequence = fields.Integer("sequence", default=10)
    short_code = fields.Char(string="Prefix")

    @api.constrains('name')
    def _check_floor_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                code = self.sudo().search(domain)
                if len(code) > 1:
                    for i in range(len(code)):
                        if code[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  The Ward Name of - %s is already exists.\n'
                                  'Please check it.....') % (
                                    record.name))


class HospitalRoom(models.Model):
    _name = "hospital.room"
    _description = "Hospital Room"

    product_id = fields.Many2one(
        "product.product",
        "Product_id",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    floor_id = fields.Many2one(
        "hospital.ward",
        "Ward No",
        help="At which floor the room is located.",
        ondelete="restrict",
    )
    short_code = fields.Char(string="Prefix")
    room_categ_id = fields.Many2one(
        "hospital.room.type", "Room Category", required=True, ondelete="restrict"
    )
    room_amenities_ids = fields.Many2many(
        "hospital.room.amenities", string="Room Amenities", help="List of room amenities."
    )
    status = fields.Selection(
        [('book', 'Booked'), ("available", "Available"), ("occupied", "Occupied")],
        default="available",
    )
    room_no = fields.Char(string="Room No")
    product_manager = fields.Many2one("res.users")
    image = fields.Binary('Upload Image')
    image1 = fields.Binary('Upload Image')
    image2 = fields.Binary('Upload Image')
    image3 = fields.Binary('Upload Image')
    image4 = fields.Binary('Upload Image')
    image5 = fields.Binary('Upload Image')
    image6 = fields.Binary('Upload Image')

    def generate_hotel_room_sequence(self):
        if self.room_categ_id or self.floor_id:
            floor = self.floor_id.short_code
            room = self.short_code
            room_number = str(floor) + '/' + str(room) + '/' + str(self.room_no)
            if self.room_no and floor and room:
                self.room_no = room_number
            else:
                raise ValidationError(
                    _('Alert !!  Mr.%s - The Room is Not mentioned the Room Category,Ward & Room Prefix.\n'
                      'Please check it.....') % (
                        self.env.user.name))


class HospitalRoomType(models.Model):
    _name = "hospital.room.type"
    _description = "Room Type"

    categ_id = fields.Many2one("hospital.room.type", "Category")
    product_categ_id = fields.Many2one(
        "product.category",
        "Product Category",
        delegate=True,
        required=True,
        copy=False,
        ondelete="restrict",
    )
    short_code = fields.Char(string="Prefix")

    @api.constrains('name')
    def _check_room_type_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                code = self.sudo().search(domain)
                if len(code) > 1:
                    for i in range(len(code)):
                        if code[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  The Room Type of - %s is already exists.\n'
                                  'Please check it.....') % (
                                    record.name))

    @api.model
    def create(self, vals):
        if "categ_id" in vals:
            room_categ = self.env["hospital.room.type"].browse(vals.get("categ_id"))
            vals.update({"parent_id": room_categ.product_categ_id.id})
        return super(HospitalRoomType, self).create(vals)

    def write(self, vals):
        if "categ_id" in vals:
            room_categ = self.env["hospital.room.type"].browse(vals.get("categ_id"))
            vals.update({"parent_id": room_categ.product_categ_id.id})
        return super(HospitalRoomType, self).write(vals)

    def name_get(self):
        def get_names(cat):
            """Return the list [cat.name, cat.categ_id.name, ...]"""
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.categ_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symmetric to name_get
            category_names = name.split(" / ")
            parents = list(category_names)
            child = parents.pop()
            domain = [("name", operator, child)]
            if parents:
                names_ids = self.name_search(
                    " / ".join(parents),
                    args=args,
                    operator="ilike",
                    limit=limit,
                )
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([("id", "not in", category_ids)])
                    domain = expression.OR(
                        [[("categ_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("categ_id", "in", category_ids)], domain]
                    )
                for i in range(1, len(category_names)):
                    domain = [
                        [
                            (
                                "name",
                                operator,
                                " / ".join(category_names[-1 - i:]),
                            )
                        ],
                        domain,
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class HospitalRoomAmenitiesType(models.Model):
    _name = "hospital.room.amenities.type"
    _description = "Hospital Amenities Type"

    amenity_id = fields.Many2one("hospital.room.amenities.type", "Category")
    child_ids = fields.One2many(
        "hospital.room.amenities.type", "amenity_id", "Amenities Categories"
    )
    product_categ_id = fields.Many2one(
        "product.category",
        "Product Category",
        delegate=True,
        required=True,
        copy=False,
        ondelete="restrict",
    )

    @api.constrains('name')
    def _check_room_amenities_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                code = self.sudo().search(domain)
                if len(code) > 1:
                    for i in range(len(code)):
                        if code[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  The Amenity Type of - %s is already exists.\n'
                                  'Please check it.....') % (
                                    record.name))

    @api.model
    def create(self, vals):
        if "amenity_id" in vals:
            amenity_categ = self.env["hospital.room.amenities.type"].browse(
                vals.get("amenity_id")
            )
            vals.update({"parent_id": amenity_categ.product_categ_id.id})
        return super(HospitalRoomAmenitiesType, self).create(vals)

    def write(self, vals):
        if "amenity_id" in vals:
            amenity_categ = self.env["hospital.room.amenities.type"].browse(
                vals.get("amenity_id")
            )
            vals.update({"parent_id": amenity_categ.product_categ_id.id})
        return super(HospitalRoomAmenitiesType, self).write(vals)

    def name_get(self):
        def get_names(cat):
            """Return the list [cat.name, cat.amenity_id.name, ...]"""
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.amenity_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(" / ")
            parents = list(category_names)
            child = parents.pop()
            domain = [("name", operator, child)]
            if parents:
                names_ids = self.name_search(
                    " / ".join(parents),
                    args=args,
                    operator="ilike",
                    limit=limit,
                )
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([("id", "not in", category_ids)])
                    domain = expression.OR(
                        [[("amenity_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("amenity_id", "in", category_ids)], domain]
                    )
                for i in range(1, len(category_names)):
                    domain = [
                        [
                            (
                                "name",
                                operator,
                                " / ".join(category_names[-1 - i:]),
                            )
                        ],
                        domain,
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class HospitalRoomAmenities(models.Model):
    _name = "hospital.room.amenities"
    _description = "Hospital Room amenities"

    product_id = fields.Many2one(
        "product.product",
        "Room Amenities Product",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    amenities_categ_id = fields.Many2one(
        "hospital.room.amenities.type",
        "Amenities Category",
        required=True,
        ondelete="restrict",
    )
    product_manager = fields.Many2one("res.users")

    @api.model
    def create(self, vals):
        if "amenities_categ_id" in vals:
            amenities_categ = self.env["hospital.room.amenities.type"].browse(
                vals.get("amenities_categ_id")
            )
            vals.update({"categ_id": amenities_categ.product_categ_id.id})
        return super(HospitalRoomAmenities, self).create(vals)

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "amenities_categ_id" in vals:
            amenities_categ = self.env["hospital.room.amenities.type"].browse(
                vals.get("amenities_categ_id")
            )
            vals.update({"categ_id": amenities_categ.product_categ_id.id})
        return super(HospitalRoomAmenities, self).write(vals)

    @api.constrains('name')
    def _check_room_amenity_name(self):
        for record in self:
            if record.name:
                domain = [('name', '=', record.name)]
                code = self.sudo().search(domain)
                if len(code) > 1:
                    for i in range(len(code)):
                        if code[i].id != record.id:
                            raise ValidationError(
                                _('Alert !!  The Room Amenity of - %s is already exists.\n'
                                  'Please check it.....') % (
                                    record.name))
