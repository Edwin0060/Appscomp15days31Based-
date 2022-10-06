# -*- coding: utf-8 -*-
{
    'name': "Employee Resume Report",
    'summary': """
        This module serves to generate employee resume reports that can be used as your company's archive document""",
    'author': "Kelvzxu",
    'website': "https://www.kltech-intl.com/",
    'category': 'Human Resources',
    'version': '0.1',
    'license': 'GPL-3',
    'depends': ['hr','hr_skills',],
    'data': [
        'views/resume_report_template.xml',
        'report/hr_advance_report.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
}
