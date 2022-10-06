# -*- coding: utf-8 -*-
# from odoo import http


# class EducationHistory(http.Controller):
#     @http.route('/education_history/education_history/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/education_history/education_history/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('education_history.listing', {
#             'root': '/education_history/education_history',
#             'objects': http.request.env['education_history.education_history'].search([]),
#         })

#     @http.route('/education_history/education_history/objects/<model("education_history.education_history"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('education_history.object', {
#             'object': obj
#         })
