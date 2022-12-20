# -*- coding: utf-8 -*-
{
    'name': 'Product Report',
    'version': '15.0.0.1',
    'summary': 'POS order wise Product',
    'category': 'Sale',
    'author': 'Eddie',
    'company': 'Appscomp',
    'depends': ['point_of_sale', 'pos_sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_pos_order.xml',
        'views/pos_order.xml',
        'report/product_report_template_menu.xml',
        'report/template_wizard_product_report.xml',
    ],
    'license': 'AGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
