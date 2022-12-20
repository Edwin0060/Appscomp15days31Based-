# -*- coding: utf-8 -*-
{
    'name': "POS Low Stock Alert",
    'summary': """Manage the Stock of your POS products by highlighting them in different colors depending on
                their stock state.""",
    'description': """
        POS Low Stock Alert v15.0
        Manage the Stock of your POS products by highlighting them in different colors depending on
                their stock state.
        POS,
        POS Low Stock Alert,
        Low Stock Alert,
        Stock Alert,
        POS Low Stock Warning,
        POS Stock Warning,
        Inventory Alert,
        Inventory Minimum Quantity Alert,
        Inventory Minimum Quantity Warning,
        POS Manager,
        POS Inventory,
        POS Stock,
        POS Stock Alert,
        POS Retail,
        POS Shop,
        Point of Sales,
        Point of Sales Stock Alert,
        Point of Sales Low Stock Alert,
        POS Shop Low Stock,
        stock notification, 
        low stock notification, 
        product stock notification, 
        product low stock, 
        stock management, 
        notification odoo apps, 
        odoo notification, 
        odoo website stock, 
        website stock notify, 
        stock notify, 
        product stock, 
        odoo website product stock, 
        odoo website stock management
    """,
    'author': 'Ksolves India Ltd.',
    'website': "https://www.ksolves.com/",
    'license': 'LGPL-3',
    'currency': 'EUR',
    'price': '0.0',
    'category': 'Point Of Sale',
    'support': 'sales@ksolves.com',
    'version': '15.0.1.0.0',
    'images': ['static/description/pos_15.jpg'],
    'depends': ['point_of_sale'],
    'data': [
        # 'views/assets.xml',
        'views/config.xml',
        'views/sales_pos_report.xml'
    ],
    # 'qweb': ['static/src/xml/ks_low_stock.xml']
    'assets' : {
        'point_of_sale.assets': [
            'ks_pos_low_stock_alert/static/src/css/ks_low_stock.css',
            'ks_pos_low_stock_alert/static/src/js/ks_utils.js',
            'ks_pos_low_stock_alert/static/src/js/ks_low_stock.js',
            'ks_pos_low_stock_alert/static/src/js/ks_product_list.js',
            'ks_pos_low_stock_alert/static/src/js/ks_product_screen.js',
        ],
        'web.assets_qweb': [
            'ks_pos_low_stock_alert/static/src/xml/**/*',
        ]
    }
}
