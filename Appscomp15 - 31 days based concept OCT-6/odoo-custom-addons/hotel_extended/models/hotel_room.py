# See LICENSE file for full copyright and licensing details.
import logging

from datetime import date
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt

_logger = logging.getLogger(__name__)
try:
    import pytz
except (ImportError, IOError) as err:
    _logger.debug(err)


class HotelRoom(models.Model):

    _inherit = "hotel.room"
    _description = "Hotel Room"

    room_reservation_line_ids = fields.One2many(
        "hotel.room.reservation.line", "room_id", string="Room Reserve Line"
    )


    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for room in self:
            for reserv_line in room.room_reservation_line_ids:
                if reserv_line.status == "confirm":
                    raise ValidationError(
                        _(
                            """Alert!, User is not able to delete the """
                            """room after the room in %s state """
                            """in reservation"""
                        )
                        % (reserv_line.status)
                    )
        return super(HotelRoom, self).unlink()

    @api.model
    def cron_room_line(self):
        """
        This method is for scheduler
        every 1min scheduler will call this method and check Status of
        room is occupied or available
        --------------------------------------------------------------
        @param self: The object pointer
        @return: update status of hotel room reservation line
        """
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        folio_room_line_obj = self.env["folio.room.line"]
        curr_date = fields.Datetime.now().strftime(dt)
        for room in self.search([]):
            reserv_line_ids = room.room_reservation_line_ids.ids
            reservation_line_ids = reservation_line_obj.search(
                [
                    ("id", "in", reserv_line_ids),
                    ("check_in", "<=", curr_date),
                    ("check_out", ">=", curr_date),
                ]
            )
            rooms_ids = room.room_line_ids.ids
            room_line_ids = folio_room_line_obj.search(
                [
                    ("id", "in", rooms_ids),
                    ("check_in", "<=", curr_date),
                    ("check_out", ">=", curr_date),
                ]
            )
            status = {"isroom": True, "color": 5}
            if reservation_line_ids:
                status = {"isroom": False, "color": 2}
            room.write(status)
            if room_line_ids:
                status = {"isroom": False, "color": 2}
            room.write(status)
            if reservation_line_ids and room_line_ids:
                raise ValidationError(
                    _("Please Check Rooms Status for %s.") % room.name
                )
        return True


class RoomReservationSummary(models.Model):

    _name = "room.reservation.summary"
    _description = "Room reservation summary"

    name = fields.Char("Reservation Summary", default="Reservations Summary")
    date_from = fields.Datetime("Date From", default=lambda self: fields.Date.today())
    date_to = fields.Datetime(
        "Date To",
        default=lambda self: fields.Date.today() + relativedelta(days=30),
    )
    room_categ_id = fields.Many2many(
        "hotel.floor", string="Floor Category", ondelete="restrict"
    )
    room_name = fields.Many2many("hotel.room",string="Room Number")

    summary_header = fields.Text("Summary Header")
    room_summary = fields.Text("Room Summary")


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

    def button_room_summary_refresh(self):
        self.get_room_summary()
        self.date_to += timedelta(seconds=1)

    @api.onchange("date_from", "date_to","room_categ_id","room_name","room_summary")  # noqa C901 (function is too complex)
    def get_room_summary(self):  # noqa C901 (function is too complex)
        """
        @param self: object pointer
        """
        global reservation_id
        res = {}
        all_detail = []
        room_obj = self.env["hotel.room"]
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        folio_room_line_obj = self.env["folio.room.line"]
        user_obj = self.env["res.users"]
        date_range_list = []
        main_header = []
        # summary_header_list = ["Floor","Rooms"]
        summary_header_list = ["Rooms"]
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise UserError(_("Checkout date should be greater than Checkin date."))
            if self._context.get("tz", False):
                timezone = pytz.timezone(self._context.get("tz", False))
            else:
                timezone = pytz.timezone("UTC")
            d_frm_obj = (
                self.date_from
                .replace(tzinfo=pytz.timezone("UTC"))
                .astimezone(timezone)
            )
            d_to_obj = (
                self.date_to.replace(tzinfo=pytz.timezone("UTC")).astimezone(timezone)
            )
            temp_date = d_frm_obj
            while temp_date <= d_to_obj:
                val = ""
                val = (
                    str(temp_date.strftime("%a"))
                    + " "
                    + str(temp_date.strftime("%b"))
                    + " "
                    + str(temp_date.strftime("%d"))
                )
                summary_header_list.append(val)
                temp_date = temp_date + timedelta(days=1)
                date_range_list.append(temp_date.strftime(dt))

            all_detail.append(summary_header_list)
            domain = []

            if self.room_categ_id:
                domain = [('floor_id', '=', self.room_categ_id.ids)]
                if self.room_name:
                    domain = [('floor_id', '=', self.room_categ_id.ids),('name', '=', self.room_name.name)]
            elif self.room_name:
                domain = [('name', '=', self.room_name.name)]

            all_room_detail = []
            if self.room_categ_id or self.room_name:
                room_ids = room_obj.search(domain)
                for room in room_ids:
                    room_detail = {}
                    room_list_stats = []
                    room_detail.update({"floor": room.floor_id.name or "","name": room.name or ""})
                    if not room.room_reservation_line_ids and not room.room_line_ids:
                        for chk_date in date_range_list:
                            room_list_stats.append(
                                {
                                    "state": "Free",
                                    "date": chk_date,
                                    "box_date": str(chk_date).split(" ")[0],
                                    "room_id": room.id,
                                    "floor_id": room.floor_id.id,
                                }
                            )
                    else:
                        import datetime
                        for chk_date in date_range_list:
                            reserve_draft_id = self.env["hotel.reservation"].search(
                                [
                                    ("checkin", "<=", chk_date),
                                    ("checkout", ">=", chk_date),
                                    ("state", "=", "draft"),
                                ]
                            )
                            ch_dt = chk_date[:10] + " 23:59:59"
                            ttime = datetime.datetime.strptime(ch_dt, dt)
                            c = ttime.replace(tzinfo=timezone).astimezone(
                                pytz.timezone("UTC")
                            )
                            chk_date = c.strftime(dt)
                            reserline_ids = room.room_reservation_line_ids.ids
                            reservline_ids = reservation_line_obj.search(
                                [
                                    ("id", "in", reserline_ids),
                                    ("check_in", "<=", chk_date),
                                    ("check_out", ">=", chk_date),
                                    ("state", "=", "assigned"),
                                ]
                            )
                            if not reservline_ids:
                                sdt = dt
                                chk_date = datetime.datetime.strptime(chk_date, sdt)
                                chk_date = datetime.datetime.strftime(
                                    chk_date - timedelta(days=1), sdt
                                )
                                reservline_ids = reservation_line_obj.search(
                                    [
                                        ("id", "in", reserline_ids),
                                        ("check_in", "<=", chk_date),
                                        ("check_out", ">=", chk_date),
                                        ("state", "=", "assigned"),
                                    ]
                                )
                                for res_room in reservline_ids:
                                    cid = res_room.check_in
                                    cod = res_room.check_out
                                    dur = cod - cid
                                    if room_list_stats:
                                        count = 0
                                        for rlist in room_list_stats:
                                            cidst = datetime.strftime(cid, dt)
                                            codst = datetime.strftime(cod, dt)
                                            rm_id = res_room.room_id.id
                                            ci = rlist.get("date") >= cidst
                                            co = rlist.get("date") <= codst
                                            rm = rlist.get("room_id") == rm_id
                                            st = rlist.get("state") == "Reserved"
                                            if ci and co and rm and st:
                                                count += 1
                                        if count - dur.days == 0:
                                            c_id1 = user_obj.browse(self._uid)
                                            c_id = c_id1.company_id
                                            con_add = 0
                                            amin = 0.0
                                            # When configured_addition_hours is
                                            # greater than zero then we calculate
                                            # additional minutes
                                            if c_id:
                                                con_add = c_id.additional_hours
                                            if con_add > 0:
                                                amin = abs(con_add * 60)
                                            hr_dur = abs(dur.seconds / 60)
                                            if amin > 0:
                                                # When additional minutes is greater
                                                # than zero then check duration with
                                                # extra minutes and give the room
                                                # reservation status is reserved
                                                # --------------------------
                                                if hr_dur >= amin:
                                                    reservline_ids = True
                                                else:
                                                    reservline_ids = False
                                            else:
                                                if hr_dur > 0:
                                                    reservline_ids = True
                                                else:
                                                    reservline_ids = False
                                        else:
                                            reservline_ids = False
                            fol_room_line_ids = room.room_line_ids.ids
                            chk_state = ["draft", "cancel"]
                            folio_resrv_ids = folio_room_line_obj.search(
                                [
                                    ("id", "in", fol_room_line_ids),
                                    ("check_in", "<=", chk_date),
                                    ("check_out", ">=", chk_date),
                                    ("status", "not in", chk_state),
                                ]
                            )
                            if reservline_ids or folio_resrv_ids:
                                if hasattr(reservline_ids, 'reservation_id') and reservline_ids.reservation_id:
                                    reservation_id = reservline_ids.reservation_id
                                room_list_stats.append(
                                    {
                                        "state": "Reserved",
                                        "date": chk_date,
                                        "box_date": str(chk_date).split(" ")[0],
                                        "room_id": room.id,
                                        "floor_id": room.floor_id.id,
                                        "is_draft": "No",
                                        "data_model": "",
                                        "data_id": reservation_id.id or 0,
                                    }
                                )
                            elif reserve_draft_id:
                                room_list_stats.append(
                                    {
                                        "state": "Draft",
                                        "date": chk_date,
                                        "box_date": str(chk_date).split(" ")[0],
                                        "room_id": room.id,
                                        "is_draft": "Yes",
                                        "data_model": "",
                                        "data_id": 0,
                                    }
                                )
                            else:
                                room_list_stats.append(
                                    {
                                        "state": "Free",
                                        "date": chk_date,
                                        "box_date": str(chk_date).split(" ")[0],
                                        "room_id": room.id,
                                        "floor_id": room.floor_id.id,
                                    }
                                )

                    room_detail.update({"value": room_list_stats})
                    all_room_detail.append(room_detail)
            else:
                import datetime
                room_ids = room_obj.search([])
                for room in room_ids:
                    room_detail = {}
                    room_list_stats = []
                    room_detail.update({"floor": room.floor_id.name or "", "name": room.name or ""})
                    if not room.room_reservation_line_ids and not room.room_line_ids:
                        for chk_date in date_range_list:
                            datetime_object = datetime.datetime.strptime(chk_date, '%Y-%m-%d %H:%M:%S')
                            datetime_object =datetime_object- timedelta(hours=24, minutes=00)
                            # print(datetime_object)
                            chk_date = str(datetime_object)
                            room_list_stats.append(
                                {
                                    "state": "Free",
                                    "date": chk_date,
                                    "box_date": str(chk_date).split(" ")[0],
                                    "room_id": room.id,
                                    "floor_id": room.floor_id.id,
                                }
                            )
                    else:
                        import datetime
                        for chk_date in date_range_list:

                            reserve_draft_id = self.env["hotel.reservation"].search(
                                [
                                    ("checkin", "<=", chk_date),
                                    ("checkout", ">=", chk_date),
                                    ("state", "=", "draft"),
                                ]
                            )
                            ch_dt = chk_date[:10] + " 00:00:00"
                            ttime = datetime.datetime.strptime(ch_dt, dt)
                            c = ttime.replace(tzinfo=timezone).astimezone(
                                pytz.timezone("UTC")
                            )
                            chk_date = c.strftime(dt)
                            reserline_ids = room.room_reservation_line_ids.ids
                            reservline_ids = reservation_line_obj.search(
                                [
                                    ("id", "in", reserline_ids),
                                    ("check_in", "<=", chk_date),
                                    ("check_out", ">=", chk_date),
                                    ("state", "=", "assigned"),
                                ]
                            )
                            if not reservline_ids:
                                sdt = dt
                                chk_date = datetime.datetime.strptime(chk_date, sdt)
                                # chk_date = datetime.datetime.strftime(
                                #     chk_date - timedelta(days=1), sdt
                                # )
                                reservline_ids = reservation_line_obj.search(
                                    [
                                        ("id", "in", reserline_ids),
                                        ("check_in", "<=", chk_date),
                                        ("check_out", ">=", chk_date),
                                        ("state", "=", "assigned"),
                                    ]
                                )
                                for res_room in reservline_ids:
                                    cid = res_room.check_in
                                    cod = res_room.check_out
                                    dur = cod - cid
                                    if room_list_stats:
                                        count = 0
                                        for rlist in room_list_stats:
                                            cidst = datetime.datetime.strftime(cid, dt)
                                            codst = datetime.datetime.strftime(cod, dt)
                                            rm_id = res_room.room_id.id
                                            ci = rlist.get("date") >= cidst
                                            co = rlist.get("date") <= codst
                                            rm = rlist.get("room_id") == rm_id
                                            st = rlist.get("state") == "Reserved"
                                            if ci and co and rm and st:
                                                count += 1
                                        if count - dur.days == 0:
                                            c_id1 = user_obj.browse(self._uid)
                                            c_id = c_id1.company_id
                                            con_add = 0
                                            amin = 0.0
                                            # When configured_addition_hours is
                                            # greater than zero then we calculate
                                            # additional minutes
                                            if c_id:
                                                con_add = c_id.additional_hours
                                            if con_add > 0:
                                                amin = abs(con_add * 60)
                                            hr_dur = abs(dur.seconds / 60)
                                            if amin > 0:
                                                # When additional minutes is greater
                                                # than zero then check duration with
                                                # extra minutes and give the room
                                                # reservation status is reserved
                                                # --------------------------
                                                if hr_dur >= amin:
                                                    reservline_ids = True
                                                else:
                                                    reservline_ids = False
                                            else:
                                                if hr_dur > 0:
                                                    reservline_ids = True
                                                else:
                                                    reservline_ids = False
                                        else:
                                            reservline_ids = False
                            fol_room_line_ids = room.room_line_ids.ids
                            chk_state = ["draft", "cancel"]
                            folio_resrv_ids = folio_room_line_obj.search(
                                [
                                    ("id", "in", fol_room_line_ids),
                                    ("check_in", "<=", chk_date),
                                    ("check_out", ">=", chk_date),
                                    ("status", "not in", chk_state),
                                ]
                            )
                            if str(chk_date).split(" ")[0] == str(date.today()):
                                import datetime
                                chk_date = str(datetime.datetime.now()).split(".")[0]
                            else:
                                chk_date = str(chk_date).split(" ")[0] + " 00:00:00"

                            if reservline_ids:
                                # if hasattr(reservline_ids, 'reservation_id') and reservline_ids.reservation_id:
                                reservation_id = reservline_ids.reservation_id
                                room_list_stats.append(
                                    {
                                        "state": "Reservation",
                                        "date": chk_date,
                                        "box_date": str(chk_date).split(" ")[0],
                                        "room_id": room.id,
                                        "floor_id": room.floor_id.id,
                                        "is_draft": "No",
                                        "data_model": "",
                                        "data_id": reservation_id.id or 0,
                                    }
                                )
                            elif reserve_draft_id:
                                room_list_stats.append(
                                    {
                                        "state": "Draft",
                                        "date": chk_date,
                                        "box_date": str(chk_date).split(" ")[0],
                                        "room_id": room.id,
                                        "is_draft": "Yes",
                                        "data_model": "",
                                        "data_id": 0,

                                    }
                                )
                            else:
                                room_list_stats.append(
                                    {
                                        "state": "Free",
                                        "date": chk_date,
                                        "box_date": str(chk_date).split(" ")[0],
                                        "room_id": room.id,
                                        "floor_id": room.floor_id.id,

                                    }
                                )

                    room_detail.update({"value": room_list_stats})
                    all_room_detail.append(room_detail)
            main_header.append({"header": summary_header_list})
            self.summary_header = str(main_header)
            self.room_summary = str(all_room_detail)

        return res

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            result.append((rec.room_categ_id.id, name))
        return result


