from datetime import datetime, timedelta, date
from odoo import fields, models

class TableOrderCancel(models.TransientModel):
    _name = 'housekeeping.cancel'
    _description = 'Hotel Management House Keeping Cancel Remarks'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['hotel.housekeeping'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name
        if active_id.state == 'inspect':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.room_cancel()
            active_id.write({'housekeeping_cancel_remarks': text})
        if active_id.state == 'dirty':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.room_cancel()
            active_id.write({'housekeeping_cancel_remarks_2': text})

        if active_id.state == 'clean':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.room_cancel()
            active_id.write({'housekeeping_cancel_remarks_2': text})
        return True