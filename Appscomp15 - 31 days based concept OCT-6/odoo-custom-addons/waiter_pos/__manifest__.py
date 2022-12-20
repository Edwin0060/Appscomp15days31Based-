# -*- coding: utf-8 -*-
{
    'name': "POS Waiter",
    'author': "Appscomp Widgets Pvt Ltd",
    'website': "http://www.appscomp.com",
    'images': ['static/description/image/logo.png'],
    'category': 'Pos',
    'version': '0.1',
    'license': 'LGPL-3',
    'currency': 'EUR',
    'depends': ['base', 'point_of_sale', 'hr' , 'pos_kot'],
    'data': [
        'views/hr_employee_view_inherited.xml',
      ],
    'assets': {
        'point_of_sale.assets': [
            'waiter_pos/static/src/js/employee.js'
        ],

        'web.assets_backend': [
            'waiter_pos/static/src/js/waiter_detail.js'
        ],
        'web.assets_qweb': [
            'waiter_pos/static/src/xml/recipt.xml',
        ],
    },


}
