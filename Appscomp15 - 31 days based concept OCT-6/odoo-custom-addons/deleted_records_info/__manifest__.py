# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/
{
    'name': "Track Deleted Records",
    'summary': """
        View deleted records.""",
    'description': """
        Admin users can see which records have been deleted and by whom.
    """,
    'author': 'Aktiv Software',
    'website': 'http://www.aktivsoftware.com',
    'category': 'Extra Tools',
    'version': '14.0.1.0.0',
    'license': "AGPL-3",
    'depends': ['base_setup'],
    'data': [
        'security/deleted_records_security.xml',
        'security/ir.model.access.csv',
        'views/deleted_records_views.xml',
        'wizard/delete_records_upto_wizard_views.xml',
    ],
    'images': ['static/description/icon.jpg'],
    'sequence': 1,
    'auto_install': False,
    'installable': True,
    'application': False,
}
