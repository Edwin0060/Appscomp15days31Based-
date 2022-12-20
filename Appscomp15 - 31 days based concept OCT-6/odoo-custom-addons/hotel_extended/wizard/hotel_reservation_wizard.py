# See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from datetime import datetime, timedelta, date
import datetime


class HotelReservationWizard(models.TransientModel):
    _name = "hotel.reservation.wizard"
    _description = "Allow to generate a reservation"

    date_start = fields.Datetime("Start Date", required=True)
    date_end = fields.Datetime("End Date", required=True)

    def report_reservation_detail(self):
        data = {
            "ids": self.ids,
            "model": "hotel.reservation",
            "form": self.read(["date_start", "date_end"])[0],
        }
        print('******************************************', data )

        return self.env.ref("hotel_extended.hotel_roomres_details").report_action(
            self, data=data
        )

    def report_checkin_detail(self):
        data = {
            "ids": self.ids,
            "model": "hotel.reservation",
            "form": self.read(["date_start", "date_end"])[0],
        }

        return self.env.ref("hotel_extended.hotel_checkin_details").report_action(
            self, data=data
        )

    #
    def report_checkout_detail(self):
        data = {
            "ids": self.ids,
            "model": "hotel.reservation",
            "form": self.read(["date_start", "date_end"])[0],
        }
        return self.env.ref("hotel_extended.hotel_checkout_details").report_action(
            self, data=data
        )

    def report_maxroom_detail(self):
        data = {
            "ids": self.ids,
            "model": "hotel.reservation",
            "form": self.read(["date_start", "date_end"])[0],
        }
        return self.env.ref("hotel_extended.hotel_maxroom_details").report_action(
            self, data=data
        )


class MakeFolioWizard(models.TransientModel):
    _name = "wizard.make.folio"
    _description = "Allow to generate the folio"

    grouped = fields.Boolean("Group the Proformas")

    def make_folios(self):
        reservation_obj = self.env["hotel.reservation"]
        newinv = [
            order.id
            for order in reservation_obj.browse(
                self.env.context.get("active_ids", [])
            ).mapped("folio_id")
        ]
        return {
            "domain": "[('id','in', [" + ",".join(map(str, newinv)) + "])]",
            "name": "Proforma",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "hotel.folio",
            "view_id": False,
            "type": "ir.actions.act_window",
        }


class NewQuickReservationWizard(models.TransientModel):
    _name = "new.quick.reservation.wizard"
    _description = "New Quick Reservation Wizard"

    name = fields.Char(string='Guest Name')
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string='E-mail')
    valid_proof = fields.Many2one("identity.register", "Proof Type")
    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High')],
        string='Priority')

    def create_new_guest(self):
        view_id = self.sudo().env['quick.room.reservation']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Guest Quick Reservation',
            'res_model': 'quick.room.reservation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('hotel_extended.quick_room_reservation_form_view', False).id,
            'target': 'new',
        }



class TableOrderCancel(models.TransientModel):
    _name = 'hotel.management.cancel.remarks'
    _description = 'Hotel Management Reservations Cancel Remarks'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['hotel.reservation'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name
        if active_id.state == 'confirm':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.cancel_reservation()
            active_id.write({'reservation_cancel_remarks': text})

        return True
class ForceCloseWizard(models.TransientModel):
    _name = 'hotel.proforma.force.close'
    _description = 'Hotel Management Reservations Cancel Force Close Remarks'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')
    checkin_time = fields.Char("Check In Time")

    # @api.depands('')

    def show_checkin_time(self):
        now = str(datetime.datetime.now()).split('.')[0]
        self.checkin_time=now
    def tick_ok(self):

        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['hotel.folio'].search([('id', '=', applicant_id)])
        now = str(datetime.datetime.now()).split('.')[0]
        current_user = self.env.user.name
        text = '[ ' + current_user + ' ]' + '[ ' + now + ' ]' + ' - ' + self.remarks + '\n'
        active_id.write({'cancel_remarks': text})
        active_id.write({'state': 'short'})
        vals = {
            "check_out": now,
        }
        print(active_id.name)
        for i in active_id.room_line_ids:
            reservation = self.env['hotel.reservation'].search([('reservation_no', '=',active_id.reservation_id.reservation_no)])
            reservation.write({'checkout':now})
            values = {
                'actual_checkout': now,
            }
            active_id.room_line_ids.update(values)
            room = self.env['hotel.room'].search([('name', '=', i.product_id.name)])
            line_ids = room.room_reservation_line_ids.search([('reservation_id', '=', active_id.reservation_id.id)])
            line_folio_ids = room.room_line_ids.search([('folio_id', '=', active_id.id)])
            line_ids.sudo().update(vals)
            line_folio_ids.sudo().update(vals)
        return True
