from odoo import fields, models, api, _

class Project(models.Model):
    _inherit = "project.project"

    project_team_leader = fields.Many2one('hr.employee', string="Project Leader", tracking=True)
