# -*- coding: utf-8 -*-
{
    'name': "Employee Education Records",

    'summary': """
        Manage Employee Education Record""",

    'description': """
        Manage Employee Education Record
    """,

    'author': "HAK Solutions",
    'maintainer': 'hunainfast@gmail.com',
    'website': "http://www.haksolutions.com",
      'license': 'AGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'images': ['static/description/icon.png'],
}
