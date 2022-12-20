# -*- coding: utf-8 -*-
import os
import base64
import pyscreenshot as ImageGrab
from odoo import api, models

# the list of models data which are to be skipped in the deleted records list.
SKIPPEDTABLELIST = ['deleted.records', 'ir.attachment',
                    'mail.followers', 'mail.message', 'mail.mail', 'ir.model.data']


class BaseModelExtend(models.AbstractModel):
    _inherit = 'base'

    def unlink(self):
        # common unlink method override.
        deleted_recs = self.env['deleted.records']

        ''' If user will delete records from below list than history record will
            created '''

        if self and not self._transient and self._name not in SKIPPEDTABLELIST:
            ''' It will take screenshot if any user delete any records.
            So admin user can view deleted records data.'''
            screenshot = ImageGrab.grab()
            screenshot.save('/tmp/screenshot.png')

            model_name = self._name
            # Fetch models id of deleted record.
            model_rec = self.env['ir.model'].sudo().search(
                [('model', '=', model_name)])
            '''Get display name of deleted records to write in
                deleted_records models.'''
            for rec in self:
                name = False
                if rec._fields.get('name'):
                    if rec.name:
                        name = rec.name + ', ' + str(rec.id)
                if not name and self._fields.get('display_name'):
                    if rec.display_name:
                        name = rec.display_name + ', ' + str(rec.id)
                if not name and self._rec_name:
                    sql_query = '''SELECT %s from %s where id = %s'''
                    params = (self._rec_name, self._table, rec.id)
                    self.env.cr.execute(sql_query, params)
                    results = self.env.cr.dictfetchall()
                    name = results[0].get(self._rec_name)
                    name += ', ' + str(rec.id)

                # Created deleted history record.
                deleted_rec = deleted_recs.sudo().create(
                    {'name': name,
                     'model_id': model_rec.id,
                     'user_id': self.env.user.id})
                with open("/tmp/screenshot.png", "rb") as img:
                    encode_image = base64.b64encode(img.read())
                # Created attechment for deleted rec which stores screenshot.
                self.env['ir.attachment'].create(
                    {'res_model': 'deleted.records',
                     'res_id': deleted_rec.id,
                     'datas': encode_image,
                     'type': 'binary',
                     'name': name})

            # Removed screenshot from system after saving in attachment.
            os.remove("/tmp/screenshot.png")

        return super(BaseModelExtend, self).unlink()
