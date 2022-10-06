# -*- coding: utf-8 -*-
# from odoo import http


# class KotModule(http.Controller):
#     @http.route('/kot_module/kot_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kot_module/kot_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('kot_module.listing', {
#             'root': '/kot_module/kot_module',
#             'objects': http.request.env['kot_module.kot_module'].search([]),
#         })

#     @http.route('/kot_module/kot_module/objects/<model("kot_module.kot_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kot_module.object', {
#             'object': obj
#         })
