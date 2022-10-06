# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Exit Process Management',
    'version': '15.0',
    'license': 'Other proprietary',
    'category': 'Human Resources',
    'summary': 'Employee Out/Exit/Termination Process Management',
    'description': """
        Employee Exit process:
            ---> Configure CheckLists
            ---> Employee Exit Request
            ---> Employee Exit Checklists
            ---> Print Employee Exit Report 

Tags:
exit process
employee exit process
employee termination process
employee leave process
employee leave company
employee exit company
hr exit process
human resource exit process
checklist for exit process
Termination terminate
            """,
    'author': 'Edwin M',
    'website': 'http://www.appscomp.com/',
    'depends': ['hr', 'hr_contract', 'calendar'],
    'data': [
            'security/hr_exit_security.xml',
            'security/ir.model.access.csv',
            'data/mail_template.xml',
            'views/hr_exit_view.xml',
            'views/hr_employee_view.xml',
            'report/hr_exit_process_report.xml',
             ],
    'installable': True,
    'application': True,
}

