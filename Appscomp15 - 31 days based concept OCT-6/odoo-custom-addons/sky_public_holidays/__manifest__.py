# -*- encoding: utf-8 -*-
##############################################################################
#
#    Skyscend Business Solutions
#    Copyright (C) 2019 (http://www.skyscendbs.com)
#
##############################################################################
{
    'name': 'Public Holidays',
    'version': '13.0.0.1',
    'category': 'HR',
    'license': 'AGPL-3',
    'description': """
    This module is used to define public holidays for the year
    """,
    'author': 'Skyscend Business Solutions',
    'website': 'http://www.skyscendbs.com',
    'depends': ['hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_public_holidays_view.xml',
        'report/public_holiday_report.xml',
        'report/report_register.xml',
        'data/public_holiday_template.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False
}
