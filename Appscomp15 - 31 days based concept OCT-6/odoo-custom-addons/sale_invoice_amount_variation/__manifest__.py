# -*- coding: utf-8 -*-
{
    'name': "Update Sale Invoice Amount",
    'summary': """
        Prints report which shows unit price changed, sale price, difference and the user who has done changes.
       """,
    'author': "Nithish Kumar R",
    'website': "http://www.appscomp.com",
    'license': "AGPL-3",
    'category': 'Accounting',
    'version': '15.0.1.0.0',
    'depends': ['sale', 'account', 'stock'],
    'data': [
        'views/account_invoice_line_views.xml',
        #'views/account_invoice.xml',
        # 'views/report_invoice.xml'
    ],
    'images': [
        'static/description/banner.jpg',
    ],
    'auto_install': False,
    'installable': True,
    'application': False
}
