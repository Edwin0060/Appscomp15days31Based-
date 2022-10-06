from odoo import fields, models, api, _


class ProjectProject(models.Model):
    _inherit = "project.project"
    _description = 'Project'

    project_team_leader = fields.Many2one('hr.employee', string="Project Leader", tracking=True)
