{
    'name' : 'POS Rounding Amount App',
    'author': "Edge Technologies",
    'version' : '15.0.0.0',
    'live_test_url':'https://youtu.be/6TrqClPUg0E',
    "images":["static/description/main_screenshot.png"],
    'summary' : 'App allow Point of sales Rounding Off Amount for order in point of sales bill amount POS Payment Screen pos manual rounding off pos automatic rounding POS Rounding Payment POS Rounding orders pos Auto Rounding pos Rounding amount value',
    'description' : """

     This module helps to Round Total amount in POS .
     Rounding Off amount in POS Bill almost become necessary, specially amount shown in screen for product make it harder for cashier to keep change that amount and make it frustrating for pos user when you have big line behind    This Odoo Point of sales App allow Rounding Off Amount and value of products in POS order and consider rounded off amount as product for that order in point of sales bill amount . User Doesn't need to do any back end configuration for that you can simple  POS Payment Screen to pos manual rounding off amount or you can allow automatic rounding in point of sales Odoo app.POS Order Rounding Amount App helps to Round Total amount in POS Order, POS Receipt, Invoice and Journal Entries.

    """,
    'depends' : ['base','point_of_sale','account','stock'],
    "license" : "OPL-1",
    'data' : [
        'views/pos_order_total_round_config.xml',
    ],

    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_order_total_rounding_app/static/src/js/screens.js',
        ],
        'web.assets_qweb': [
            'pos_order_total_rounding_app/static/src/xml/pos_product_view.xml',
        ],
    },
   
    'installable' : True,
    'auto_install' : False,  
    "price": 15,
    "currency": 'EUR',
    'category' : "Point of Sales",
}
