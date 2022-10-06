# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>)

{
    'name': 'Birthday Notification',
    'version': '15.0.1.0',
    'summary': 'Birthday Wishes to Employees & Contacts',
    'description': """
    This module send email notification for birthday wish to employees and contacts.

    Birthday blessings
    Birthday card
    Birthday cheer
    Birthday notification
    Birthday greeting
    Birthday message
    Birthday reminder
    Birthday wishes
    Bliss
    Email notification
    Joyous occasion
    Moment
    Special day
    Wishes
    Your day
    """,
    'category': 'Tools',
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'depends': ['base_setup', 'hr', 'contacts'],
    'images': ['static/description/banner.jpg'],
    'data': [
        'data/knk_mail_data.xml',
        'data/knk_cron_data.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
