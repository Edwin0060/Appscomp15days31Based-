{
    'name': "Hospital Dashboard",
    'version': "15.0.1.0.0",
    'category': "Tools",
    'summary': """
        Hospital Dashboard
    """,
    'author': 'Appscomp Odoo Team',
    'company': 'Appscomp Widget Pvt Ltd',
    'maintainer': '',
    'website': "",
    'data': [
        'data/dashboard_cron.xml',
        'views/dashboard_menu.xml',
    ],
    'images': ['static/description/banner.png'],
    'depends': ['web', 'basic_hms'],
    "assets": {
        "web.assets_backend": [
            "dashboard/static/src/js/dashboard.js",
            "dashboard/static/src/css/dashboard.css",
        ],

        'web.assets_qweb': [
            "dashboard/views/dashboard_menu.xml",
            "dashboard/static/src/xml/dashboard_template.xml"
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
