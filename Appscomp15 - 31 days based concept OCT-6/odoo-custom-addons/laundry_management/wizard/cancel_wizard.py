from odoo import fields, models
from datetime import datetime, timedelta, date



class HotelLandryOrderCancel(models.TransientModel):
    _name = 'landry.order.cancel'
    _description = 'Hotel Landry Order Cancel'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['laundry.order'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name
        if active_id.state == 'draft':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.cancel_order()
            active_id.write({'landry_cancel_remarks': text})
        if active_id.state == 'order':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.cancel_order()
            active_id.write({'landry_cancel_remarks_2': text})
        return True

class WashingOrderCancel(models.TransientModel):
    _name = 'washing.order.cancel'
    _description = 'Hotel Landry Washing Order Cancel'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def washing_tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['washing.washing'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name
        if active_id.state == 'draft':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.cancel_washing_order()
            active_id.write({'washing_cancel_remarks': text})
        if active_id.state == 'process':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.cancel_washing_order()
            active_id.write({'washing_cancel_remarks_2': text})
        return True
