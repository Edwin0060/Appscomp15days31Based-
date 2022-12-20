# -*- coding: utf-8 -*-

{
    'name': 'POS Stock',
    'category': 'Pos',
    'summary': 'User display product stock and Hide out of stock products.',
    'version': '15.0',
    'license': 'LGPL-3',
    'author': "Linescripts Softwares",
    'support': 'support@linescripts.com',
    'website': "https://www.linescripts.com",
    'description': 
    """
    User display product stock and Hide out of stock products.
    """,
    'depends': ['base','point_of_sale','stock'],
    'data': [
        'views/pos_options.xml',
    ],
    'images': ['static/description/images/pos_stock_2.jpg'],

    'assets': {
        'point_of_sale.assets': [
            '//ls_pos_stock/static/src/css/pos.css',
            '/ls_pos_stock/static/src/js/pos.js',
        ],
        'web.assets_qweb': [
            'ls_pos_stock/static/src/xml/**/*',
        ],
    },

    'price': 0.00,
  
    'installable': True,
    'application': False,
    'auto_install': False,

}

