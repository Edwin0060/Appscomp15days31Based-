{
    'name': "appscomp_hr",
    'summary': """
    Appscomp hr module customization
    """,
    'description': """
    Appscomp hr module customization
    """,
    'author': "Appscomp",
    'website': "http://www.appscomp.com",
    'category': 'Generic Modules /HR',
    'version': '14',
    'depends': ['base', 'hr','hr_skills'],
    'data': ['security/ir.model.access.csv',
             'views/hr_employee_education.xml',
             ],
    'demo': [],
    'application' : True,
}
