
{
    "name": "Hotel Housekeeping Management",
    "version": "15.0.1.0.0",
    "author": "Appscomp",
    "website": "",
    "license": "AGPL-3",
    "summary": "Manages Housekeeping Activities and its Process",
    "category": "Generic Modules/Hotel Housekeeping",
    "depends": ["hotel"],
    "demo": ["views/hotel_housekeeping_data.xml"],
    "data": [
        # "security/security.xml",
        "security/ir.model.access.csv",
        "views/report_hotel_housekeeping.xml",
        "views/hotel_housekeeping_view.xml",
        "report/hotel_housekeeping_report.xml",
        "wizard/hotel_housekeeping_wizard.xml",
        "wizard/cancel_wizard.xml",


    ],
    'assets': {
        'web.assets_qweb': [],
        'web.assets_backend': [
            'hotel_housekeeping/static/css/housekeeping.css',
        ],
    },
    "installable": True,
}
