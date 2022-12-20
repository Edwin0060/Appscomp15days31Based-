
{
    'name': "POS Kitchen Screen Dashboard",
    'version': "15.0.1.0.0",
    'category': "Tools",
    'summary': """
        Point of sale Kitchen Screen Dashboard
    """,
    'description': """
    Point of sale Kitchen Screen Dashboard
    """,
    'author': 'Appscomp Odoo Team',
    'company': 'Appscomp Widget Pvt Ltd',
    'maintainer': '',
    'website': "",
    'data': [
        'security/pos_kitchengroup.xml',
        'views/dashboard_menu_view.xml',
        'views/user_views.xml',
        'views/dashboard_kot_order_report.xml',
    ],
    'images': ['static/description/banner.png'],
    'depends': [
        'web',
        'point_of_sale',
        'pos_restaurant'
    ],
    "assets": {
        "web.assets_backend": [
            "pos_dashboard_ks/static/src/js/dashboard.js",
            "pos_dashboard_ks/static/src/css/custom.css",
        ],
        'web.assets_qweb': [
            "pos_dashboard_ks/static/src/xml/dashboard_template.xml",
            "pos_dashboard_ks/static/src/xml/Kot.xml",
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
