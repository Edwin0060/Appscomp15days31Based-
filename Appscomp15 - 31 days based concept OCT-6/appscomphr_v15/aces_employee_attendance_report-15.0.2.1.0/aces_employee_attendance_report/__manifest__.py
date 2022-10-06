{
    "name": "AnaConEx Solutions - Employee PDF Report",
    'version': '15.0.2.1.0',
    'license': 'LGPL-3',
    'sequence': 1,
    "category": "API",
    "summary": "PDF report for attendance of each employee",
    "description": """
        This module is for Attendence of employees
    """,
    "author": "AnaConEx Solutions LLC",
    "website": "https://www.anaconex.com/",
    "license": "LGPL-3",
    "depends": ['base', 'hr', 'hr_attendance'],
    "data": [
        'reports/attendance_report.xml',
        'reports/report.xml',
    ],
    "price": 0,
    "currency": 'USD',
    "images": ['static/description/banner.gif'],
    "installable": True,
    "application": True,
    "auto_install": False,
}