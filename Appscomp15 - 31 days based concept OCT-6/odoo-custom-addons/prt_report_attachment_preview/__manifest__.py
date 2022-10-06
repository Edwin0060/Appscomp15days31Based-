###################################################################################
# 
#    Copyright (C) Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

{
    "name": "Open PDF Reports and PDF Attachments in Browser",
    "version": "15.0.1.0.3",
    "summary": """Open PDF Reports and PDF Attachments in Browser""",
    "author": "Ivan Sokolov, Cetmix",
    "category": "Productivity",
    "license": "LGPL-3",
    "website": "https://cetmix.com",
    "live_test_url": "https://demo.cetmix.com",
    "description": """
    Preview reports and pdf attachments in browser instead of downloading them.
    Open Report or PDF Attachment in new tab instead of downloading.
""",
    "depends": ["web"],
    "images": ["static/description/banner.png"],
    "assets": {
        "web.assets_backend": [
            "prt_report_attachment_preview/static/src/js/action_service.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
