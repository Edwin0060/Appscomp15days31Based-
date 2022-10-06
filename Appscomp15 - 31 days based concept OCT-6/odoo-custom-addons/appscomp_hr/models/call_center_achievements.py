from odoo import models, fields, api,_, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError,UserError
from datetime import timedelta,date,datetime
from odoo import tools
from odoo.modules.module import get_module_resource
import base64
from lxml import etree
from dateutil import relativedelta
import re
import os
import json


class CallAchievments(models.Model):
    _name = 'call.achievment'
    _description = 'Call Acheivements'
    
    
    name = fields.Char(string='Ref No')
    employee_id = fields.Many2one('hr.employee',string='Employee',domain="[('work_type', '=', 'call_centre')]")
    emp_code = fields.Char(string='Employee ID')
    agent = fields.Char(string='Agent')
    date = fields.Date('Date')
    target = fields.Float(string='Target count')
    achieved_count = fields.Float(string='Achieved As Dated')
    y_beat = fields.Float(string='Yet to Beat count',compute='_target_achieved_yet')
    p_day = fields.Float(string='P Day Plan')
    current_day_count = fields.Float(string='Current Day Count')
    work_type = fields.Selection([('call_centre','Call Centre'),('it','IT'),('others','Others')],string='Team Name',default='call_centre')
    #~ week_days = fields.Selection([('sun','Sunday'),('mon','Monday'),('tue','Tuesday'),('wed','Wednesday'),('Thurs','Thursday'),('fri','Friday')],string='Working Days')
    approved = fields.Float(string='Approved')
    rejection = fields.Float(string='Rejection')
    drop = fields.Float(string='Drop')
    
    @api.onchange('employee_id','emp_code')
    def onchange_emp_no(self):
        for record in self:
            record.emp_code = record.employee_id.emp_code
            
    @api.depends('target','achieved_count','y_beat')
    def _target_achieved_yet(self):
        for record in self:
            record.y_beat = record.target - record.achieved_count
    
