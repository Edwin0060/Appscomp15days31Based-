import time

from odoo import models, fields ,api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_a_waiter = fields.Boolean(string='Is A Waiter')



class PosConfig(models.Model):
    _inherit = 'pos.config'

    waiter_configuration = fields.Boolean(string='Enable Waiter Selection')


class PosOrder(models.Model):
    _inherit = "pos.order"

    employee_id = fields.Many2one('hr.employee', string='Waiter')
    waiter_id = fields.Many2one('hr.employee', string='Waiter')
    ni_customer_contact = fields.Char(string="Waiter")

    def save_waiter(self, values):
        time.sleep(2)
        emp_id = int(values['id'])
        order_ref = f"Order {values['order_id'][0]}"
        print(order_ref)
        domain = self.env['pos.order'].search([('pos_reference','=', order_ref)])
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", values['order_id'][0],domain,emp_id)
        domain.sudo().update({
            'waiter_id': emp_id,
        })

    @api.model
    def _order_fields(self, ui_order):

        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'ni_customer_contact': ui_order['ni_customer_contact'] if ui_order.get('ni_customer_contact') else '',
        })
        return res

