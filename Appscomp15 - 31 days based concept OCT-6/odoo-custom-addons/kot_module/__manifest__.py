# -*- coding: utf-8 -*-
{
    'name': "POS KOT Current Screen Order Print",

    'summary': """
        Provides A Kitchen order Print system in pos current screen 
        iteself to take print by any printers.""",

    'description': """
        
    Provides KOT Button option in pos screen to click to view and print 
    the current pos screen orders to send to kitchen to process the order.
    """,

    'author': "Appscomp Widget Pvt Ltd",
    'website': "www.appscomp.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],
    'assets': {
        'point_of_sale.assets': [
            'kot_module/static/src/js/kot_btn_ info.js',
            'kot_module/static/src/js/Kot_order.js',
        ],

        'web.assets_backend': [
            'kot_module/static/src/js/kot.js',
        ],
        'web.assets_qweb': [
            'kot_module/static/src/views/kot_screen.xml',
            'kot_module/static/src/views/view.xml',
            'kot_module/static/src/views/kot_order.xml',

        ],

    },

}
