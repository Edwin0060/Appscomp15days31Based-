# -*- coding: utf-8 -*-

{
    'name': 'Nachi Bridal Boutique ',
    'version': '1.0.0',
    'category': 'Generic Module',
    'summary': 'Boutique Management',
    'author': 'Appscomp Widget',
    'sequence': 100,
    'description': 'This is a Boutique Shop Management which specializes in selling bridal wear',
    'data': [
        'security/ir.model.access.csv',
        'report/boutique_report.xml',
        'report/boutique_quotation.xml',
        'report/boutique_invoice_report.xml',
        'views/boutique_measurement_view.xml',
        'views/boutique_order_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'boutique_management/static/src/css/boutique_dashboard_design.css',
        ],
    },
    'depends': ['product', 'stock', 'account', 'web', 'sale', 'sale_management'],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
