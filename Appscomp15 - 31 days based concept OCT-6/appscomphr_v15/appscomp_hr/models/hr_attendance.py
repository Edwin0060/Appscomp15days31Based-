# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    parent_id = fields.Many2one(related='employee_id.parent_id', string='Reporting Head')

    #     """ Purpose : Hiding 'Administrator' record when other user login and try to view in users menu if login user has access to view users menu. """
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # print("TEAMMMMMMMMMMMMMM12344444444444")
        print(self.env.context)
        if 'team_attendance' in self.env.context and self.env.context['team_attendance']:
            # print("TEAMMMMMMMMMMMMMMMMMMMMMMMMMMM")
            res_user = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
            emp_id = self.env['hr.employee'].search([('user_id', '=', res_user.id)])
            # if len(emp_id) == 1:
            if self.env.user.has_group('asppscomp_hr.group_employee_team_leader'):
                args += [('parent_id', '=', emp_id.id)]
            # ~ if res_user.system_admin:
            # ~ args += [('id', '!=', 1)]
            # ~ else:
            # ~ args += [('id', '=', self._uid)]
        return super(HrAttendance, self).search(args, offset, limit, order, count=count)
