# -*- coding: utf-8 -*-
{
    'name': "Employee Family Information",

    'summary': "Add Employee Family Information",
    'author': "Kelvzxu",
    'website': "https://www.kltech-intl.com/",
    'category': 'Human Resources',
    'version': '0.1',
    'license': 'GPL-3',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_relation_data.xml',
        'views/hr_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
}
