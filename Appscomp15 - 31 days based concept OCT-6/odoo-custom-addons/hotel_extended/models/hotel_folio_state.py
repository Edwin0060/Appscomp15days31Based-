import datetime

from odoo import api, fields, models


class HotelFolio(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Confirm'),
        ('done', 'Done'),
        ('short', 'Short Close'),
        ('cancel', 'Cancel')
    ],
        "State",
        readonly=True,
        default="draft")


class AddProofType(models.Model):
    _inherit = 'res.partner'
    _description = 'Guest Proof Register'

    proof_type = fields.Many2one("identity.register", string="Proof Type")
    proof_img = fields.Binary(string="Proof")


class AddLinkToInvoice(models.Model):
    _inherit = 'account.payment'
    _description = 'Added Link To Invoice'

    ref_id = fields.Many2one("hotel.reservation", string="Reservation ID")


class ForceCloseReservation(models.Model):
    _inherit = 'hotel.folio'
    _description = 'Added Force Close Button'

    cancel_remarks = fields.Text(string='Force Close Remarks')

    def force_close(self):
        applicant_id = self.id
        print("++++++++++++==",applicant_id)

        view_id = self.env['folio.order.cancel']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hotel Management Reservations Force Close Remarks',
            'res_model': 'hotel.proforma.force.close',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('hotel_extended.force_close_folio_cancel_remarks_wizard', False).id,
            'target': 'new',
        }
        # active_id = self.env['hotel.folio'].search([('id', '=', applicant_id)])
        # now = str(datetime.datetime.now()).split('.')[0]
        # print("+++++++++++++++++++++++++++++",now)
        # for i in active_id.room_line_ids:
        #     print("============",i)


