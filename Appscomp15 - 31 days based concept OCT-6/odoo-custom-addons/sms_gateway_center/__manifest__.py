{
    'name': "SMS Notifications",
    'summary': """
        Sms Notifications helps you to configure multiple Twilio gateway""",
    'description': """
    """,

    'author': "Techspawn Solutions",
    'website': "http://www.techspawn.com",
    'images': ['static/description/main.gif'],

    'category': 'SMS',
    'version': '1.1',
    'depends': ['base', 'contacts'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/single_sms.xml',
        'data/cron.xml',
        'views/partner_view.xml',
        'views/partner_view_dob.xml',
        'views/gatway_auth.xml',
        'views/bulk_sms_view.xml',
        'views/bulk_history.xml',
        'views/template_view.xml',
        'views/birthday_template_view.xml',
        'views/single_sms_history.xml',
        'views/multiple_sms_group.xml',
    ],
    'currency': 'EUR',
    'demo': [
    ],
}
