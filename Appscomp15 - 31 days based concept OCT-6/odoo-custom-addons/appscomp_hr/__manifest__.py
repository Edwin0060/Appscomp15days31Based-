{
    'name': "appscomp_hr",
    'summary': """
    Appscomp hr module customization
    """,
    'description': """
    Appscomp hr module customization
    """,
    'author': "Arunagiri.K",
    'website': "http://www.appscomp.com",
    'category': 'HR',
    'version': '14',
    'depends': ['base','hr','hr_attendance','om_hr_payroll'],
    'data': ['security/appscomp_hr_security.xml',
			 'security/ir.model.access.csv',
			 'views/employee_profile.xml',
			 'views/hr_employee.xml',
			 'views/res_users.xml',
			 'views/hr_attendance_view.xml',
			 'views/call_center_views.xml',
			 'views/hr_payslip_views.xml',
			 'data/cron.xml',
    ],
    'demo': [],
}
