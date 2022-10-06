from odoo import models, api, _, fields
import urllib
from twilio.rest import Client
from odoo.exceptions import except_orm, Warning, RedirectWarning

class customer_sms(models.Model):
    _name = 'customer.sms'
    _description = 'Send SMS'

    select_template = fields.Boolean(
        string="Use Predefined Template", default=False)
    select_group = fields.Boolean(string="Use Customer Group", default=False)
    state = fields.Selection(
        [('draft', 'Draft'), ('sent', 'Sent'), ('resend', 'Resend'), ], default='draft')
    templates = fields.Many2one('template.sms', 'Template Name', default=None)
    group = fields.Many2many('multiple.sms.group', default=None)
    multi_customer = fields.Many2many(
        comodel_name='res.partner', string='Select Multiple Customers')
    to_number = fields.Char(string="Send To", required=False)
    text = fields.Text(string="Message", required=True)
    select_account = fields.Many2many(
        comodel_name='api.configure', string="Account Info", required=True)

    @api.onchange('templates')
    def onchange_template(self):
        if self.select_template == True:
            self.text = self.templates.sms_content
        else:
            self.text = None

    @api.onchange('select_template')
    def onchange_account(self):
        if self.select_template == False:
            self.templates = self.select_template
            self.text = self.text

    @api.model
    def create(self, vals):
        res = super(customer_sms, self).create(vals)
        return res

    def submit_bulk(self):
        boolean = False
        if self.text:
            msg = self.text
            select_account = self.select_account
            if self.select_group == False:
                for acc in select_account:
                    for tw_cust in self.multi_customer:
                        if acc.gateway_name == 'twilio':
                            client = Client(acc.sid, acc.auth_key)
                            try:
                                client.messages.create(
                                    body=msg, to=tw_cust.mobile, from_=acc.from_no)
                                self.state = 'sent'
                            except:
                                if tw_cust.mobile is boolean:
                                    raise Warning("Mobile Number is Not Available")
                                else:
                                    raise Warning("To number: "+tw_cust.mobile+" is incorrect mobile number")
                        else:
                            if self.multi_customer:
                                for cust in self.multi_customer:
                                    if cust.mobile:
                                        # Your authentication key.
                                        authkey = acc.auth_key
                                        # Multiple mobiles numbers separated by comma.
                                        mobiles = cust.mobile
                                        message = msg  # Your message to send.
                                        # Sender ID,While using route4 sender id should
                                        # be 6 characters long.
                                        sender = acc.sender_id_msg91
                                        route = "template"  # Define route
                                        # Prepare you post parameters
                                        values = {
                                            'authkey': authkey,
                                            'mobiles': mobiles,
                                            'message': message,
                                            'sender': sender,
                                            'route': route
                                        }
                                        # API URL
                                        url = "http://api.msg91.com/api/sendhttp.php"
                                        # URL encoding the data here.
                                        postdata = urllib.parse.urlencode(
                                            values).encode("utf-8")
                                        req = urllib.request.Request(url, postdata)
                                        response = urllib.request.urlopen(req)
                                        output = response.read()  # Get Response
            else:
                for acc in select_account:
                    for entry in self.group:
                        for each in entry:
                            for single in each.add_people:
                                if acc.gateway_name == 'twilio':
                                    client = Client(acc.sid, acc.auth_key)
                                    try:
                                        client.messages.create(
                                            body=msg, to=single.mobile, from_=acc.from_no)
                                        self.state = 'sent'
                                    except:
                                        if single.mobile is boolean:
                                            raise Warning("Mobile Number is Not Available   ")
                                        else:
                                            raise Warning("To number: "+single.mobile+" is incorrect mobile number")
                                else:
                                    if self.multi_customer:
                                        for cust in self.multi_customer:
                                            if cust.mobile:
                                                # Your authentication key.
                                                authkey = acc.auth_key
                                                # Multiple mobiles numbers separated by comma.
                                                mobiles = cust.mobile
                                                message = msg  # Your message to send.
                                                # Sender ID,While using route4 sender id should
                                                # be 6 characters long.
                                                sender = acc.sender_id_msg91
                                                route = "template"  # Define route
                                                # Prepare you post parameters
                                                values = {
                                                    'authkey': authkey,
                                                    'mobiles': mobiles,
                                                    'message': message,
                                                    'sender': sender,
                                                    'route': route
                                                }
                                                # API URL
                                                url = "http://api.msg91.com/api/sendhttp.php"
                                                # URL encoding the data here.
                                                postdata = urllib.parse.urlencode(
                                                    values).encode("utf-8")
                                                req = urllib.request.Request(url, postdata)
                                                response = urllib.request.urlopen(req)
                                                output = response.read()  # Get Response

class api_configure(models.Model):
    _name = 'api.configure'

    gateway_name = fields.Selection(
        [('twilio', 'Twilio')], string='Select Gateway', required=True, store=True, default='twilio')
    name = fields.Char(string='Sms Gateway Name', required=True, store=True)
    sid = fields.Char(string='String Identifier (SID)')
    auth_key = fields.Char(string='User Authentication key', required=True)
    from_no = fields.Char(string='From Number')
    sender_id_msg91 = fields.Char(string="Msg91 Sender ID")

    def submit_values(self):
        return {'name': self.name,
                'sid': self.sid,
                'auth_key': self.auth_key,
                'from_no': self.from_no
                }

    @api.model
    def create(self, vals):
        if vals['gateway_name'] == 'msg_91':
            if vals['sender_id_msg91'] == False:
                raise Warning('Sender Id is required')
            elif len(vals['sender_id_msg91']) > 6 or len(vals['sender_id_msg91']) < 6:
                raise Warning('Sender Id must be 6 character long is required')
        else:
            if vals['gateway_name'] == 'twilio' and vals['sid'] == False:
                raise Warning('Sid is Required')
            elif vals['gateway_name'] == 'twilio' and vals['from_no'] == False:
                raise Warning('From Number is Required')
        rec = super(api_configure, self).create(vals)
        return rec