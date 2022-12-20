
{
    'name': 'Laundry Management',
    'version': '15.0.1.0.0',
    'summary': """Complete Laundry Service Management""",
    'description': 'This module is very useful to manage all process of laundry service',
    "category": "Industries",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['base', 'mail', 'sale', 'account', 'uom', 'hotel',],
    'data': [
        'data/data.xml',
        'security/laundry_security.xml',
        'security/ir.model.access.csv',
        'wizard/cancel_wizard.xml',
        'views/laundry_view.xml',
        'views/washing_view.xml',
        'views/config_view.xml',
        'views/laundry_report.xml',
        'views/laundry_label.xml',

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
