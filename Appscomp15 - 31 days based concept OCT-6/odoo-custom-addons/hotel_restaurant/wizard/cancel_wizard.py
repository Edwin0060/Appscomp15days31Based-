from datetime import datetime, timedelta, date
from odoo import fields, models


class HotelManagementTableCancel(models.TransientModel):
    _name = 'hotel.management.table.cancel'
    _description = 'Hotel Management Cancel Remarks'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['hotel.restaurant.reservation'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name
        if active_id.state == 'draft':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.table_cancel()
            active_id.write({'table_cancel_remarks': text})
        if active_id.state == 'confirm':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.table_cancel()
            active_id.write({'table_cancel_remarks_2': text})
        return True


class HotelManagementOrderCancel(models.TransientModel):
    _name = 'hotel.management.order.cancel'
    _description = 'Hotel Management Cancel Remarks'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def order_tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['hotel.reservation.order'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name
        if active_id.state == 'draft':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.order_cancel()
            active_id.write({'order_cancel_remarks': text})
        if active_id.state == 'order':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.order_cancel()
            active_id.write({'order_cancel_remarks_2': text})
        return True


class TableOrderCancel(models.TransientModel):
    _name = 'table.order.cancel'
    _description = 'Hotel Management Cancel Remarks'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['hotel.restaurant.order'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name
        if active_id.state == 'draft':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.done_cancel()
            active_id.write({'table_order_cancel_remarks': text})
        if active_id.state == 'order':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.done_cancel()
            active_id.write({'table_order_cancel_remarks_2': text})
        return True