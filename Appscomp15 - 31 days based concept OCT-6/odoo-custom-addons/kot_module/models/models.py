# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class kot_module(models.Model):
#     _name = 'kot_module.kot_module'
#     _description = 'kot_module.kot_module'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
