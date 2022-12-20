# -*- coding: utf-8 -*-

{
    'name': 'Multiple Invoice Payments',
    'version': '15.0',
    'category': 'account',
    'author': 'ALEXMENON',
    'website': "https://appscomp.com/",

    'summary': 'Payment of multiple invoices in one screen',
    'description': """ 
            Pay multiple Customer Invoice
            Pay multiple Vendor bill
            Multiple invoice payment, 
            Invoice Multiple payment,
            Payment,
            Partial Invoice Payment,
            Full invoice Payment,
            Payment Invoice,

            Multiple Vendor Bill Payment,
            Multiple Credit note payment,
            multi payment,
            multiple payment,
         """,

    'depends': ['account'],

    'data': [
        'views/multiinvoice_payment_view.xml',
        'security/ir.model.access.csv',
    ],

    'images': [
        'static/src/img/main-screenshot.png'
    ],
    # "images":[''],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,

}

