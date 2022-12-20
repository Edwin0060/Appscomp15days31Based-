import json
from odoo import http
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class AccessToken(http.Controller):

    @http.route('/get/zomato', methods=["POST"], type="json", auth="none", csrf=False, cors=False)
    def get_zomato_orders(self, **kw):
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        if payload['order']:
            get_order = payload['order']['cartDetails']['items']['dishes']
            get_address = payload['order']['creator']['address']
            get_customer = payload['order']['creator']['name']
            get_total_amount = payload['order']['cartDetails']['subtotal']['amountDetails']['totalCost']
            all_orders = []
            for i in get_order:
                all_orders.append({
                    'name': i['name'],
                    'quantity': i['quantity'],
                    'unitCost': i['unitCost'],
                    'totalCost': i['totalCost'],
                })
            pos_order = request.env["pos.order"]
            order_line = [(5, 0, 0)]
            pos_session = request.env['pos.session'].sudo().search([('state', '=', 'opened')])
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ The pos session is called", pos_session)
            if pos_session:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!The pos session has been called")
                amount = 0
                for values in all_orders:
                    order_line.append((0, 0, {
                        'full_product_name': values['name'],
                        'product_id': 1,
                        'price_unit': values['unitCost'],
                        'discount': 0.0,
                        'qty': values['quantity'],
                        'price_subtotal': values['totalCost'],
                        'price_subtotal_incl': values['totalCost'],
                    }))
                pos_order.sudo().create({
                    'company_id': 1,
                    'name': f"Zomato/{get_customer}",
                    'pos_reference': "Zomato",
                    # 'employee_id': request.env.user.id,
                    'session_id': pos_session.id,
                    'lines': order_line,
                    'amount_total': get_total_amount,
                    'amount_tax': 0,
                    'amount_paid': 0,
                    'amount_return': 0,
                })

    @http.route('/get/swiggy', methods=["POST"], type="json", auth="none", csrf=False, cors=False)
    def get_swiggy_orders(self, **kw):
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
              payload['order']['cartDetails']['items']['dishes'])
        get_order = payload['order']['cartDetails']['items']['dishes']
        get_address = payload['order']['creator']['address']
        get_customer = payload['order']['creator']['name']
        get_total_amount = payload['order']['cartDetails']['subtotal']['amountDetails']['totalCost']
        all_orders = []
        for i in get_order:
            all_orders.append({
                'name': i['name'],
                'quantity': i['quantity'],
                'unitCost': i['unitCost'],
                'totalCost': i['totalCost'],
            })
        pos_order = request.env["pos.order"]
        order_line = [(5, 0, 0)]
        pos_session = request.env['pos.session'].sudo().search([('state', '=', 'opened')])
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ The pos session is called", pos_session)
        if pos_session:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!The pos session has been called")
            amount = 0
            for values in all_orders:
                order_line.append((0, 0, {
                    'full_product_name': values['name'],
                    'product_id': 1,
                    'price_unit': values['unitCost'],
                    'discount': 0.0,
                    'qty': values['quantity'],
                    'price_subtotal': values['totalCost'],
                    'price_subtotal_incl': values['totalCost'],
                }))
            pos_order.sudo().create({
                'company_id': 1,
                'name': f"Zomato/{get_customer}",
                'pos_reference': "Zomato",
                'employee_id': request.env.user.id,
                'session_id': pos_session.id,
                'lines': order_line,
                'amount_total': get_total_amount,
                'amount_tax': 0,
                'amount_paid': 0,
                'amount_return': 0,
            })
