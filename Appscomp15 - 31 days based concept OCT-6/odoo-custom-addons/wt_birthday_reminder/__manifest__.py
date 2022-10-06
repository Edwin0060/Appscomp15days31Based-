# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Birthday Wish to Customer and Employee",
    "version": "15.0.1.0",
    "category": "HR",
    "summary": "This Module send an email to customer and employee",
    "description": """
    This module send an email to customer and employee. also this one 
    will send reminder to all other employee and manager.
    """,
    "author": "Appscomp Widget Pvt Ltd.",
    "website": "http://appscomp.com",
    "support": "hello@appscomp.com",
    "depends": ['contacts', 'hr'],
    "data": [
        "data/ir_cron.xml",
        "data/mail_template_demo.xml"
    ],
    "images": ["images/screen_image.png"],
    "license": "OPL-1",
    "installable": True,
}
