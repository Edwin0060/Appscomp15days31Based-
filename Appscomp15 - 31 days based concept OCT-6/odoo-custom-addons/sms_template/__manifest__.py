# -*- coding: utf-8 -*-
{
    'name': "Sms Template",

    'summary': """
       Sms Template to run via cron to 
       execute the check-in and 
       check-out alert for all employees""",
    'description': """
        Sms Template to run via cron to 
       execute the check-in and 
       check-out alert for all employees
    """,
    'author': "Appscomp",
    'website': "http://www.Appscomp.com",
    'category': 'hr',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['hr'],
    # always loaded
    'data': [
        'views/hr_employee.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'assets': {
        'web.assets_frontend': [
        ],
    },
    'license': 'LGPL-3',
}
