from odoo import models, api, _, fields
import urllib
from twilio.rest import Client
from odoo.exceptions import except_orm, Warning, RedirectWarning

class send_sms_btn_single(models.TransientModel):
    _name = "customer.sms.single"
    _description = "single sms "

    select_template = fields.Boolean(string="Use Predefined Template")
    state = fields.Selection(
        [('draft', 'Draft'), ('sent', 'Sent'), ('resend', 'Resend'), ], default='draft')
    templates = fields.Many2one('template.sms', 'name', String="Template Name")
    select_template = fields.Boolean(string="Use Predefined Template")
    multi_customer = fields.Many2many(
        comodel_name='res.partner', String='Select Multiple customers')
    to_number = fields.Char(string="To Number", required=False)
    text = fields.Text(string="Message", required=True)
    select_account = fields.Many2many(
        comodel_name='api.configure', String="Account Info", required=True)

    @api.model
    def default_get(self, fields):
        res = super(send_sms_btn_single, self).default_get(fields)
        res['to_number'] = self.env['res.partner'].browse(self._context['active_id']).mobile
        res['multi_customer'] = [
            self.env['res.partner'].browse(self._context['active_id']).id]
        return res

    def _prepare_sms(self):
        res = {
            'to_number': self.to_number,
            'multi_customer': [[6, False, self.multi_customer.ids]],
            'text': self.text,
            'select_account': [[6, 0, self.select_account.ids]],
        }
        return res

    @api.onchange('templates')
    def onchange_template(self):
        self.text = self.templates.sms_content

    @api.onchange('select_template')
    def onchange_account(self):
        if self.select_template == False:
            self.templates = self.select_template
            self.text = self.text

    def submit(self):
        boolean = False
        if self.text:
            msg = self.text
            for acc in self.select_account:
                if acc.gateway_name == 'twilio':
                    client = Client(acc.sid, acc.auth_key)
                    try:
                        client.messages.create(
                            body=msg, to=self.to_number, from_=acc.from_no)
                        self.state = 'sent'
                    except:
                        if self.to_number is boolean:
                            raise Warning("Mobile Number is Not Available.")
                        raise Warning("To number: "+self.to_number+" is incorrect Mobile Number.")
                else:
                    # Your authentication key.
                    authkey = acc.auth_key
                    # Multiple mobiles numbers separated by comma.
                    mobiles = self.to_number
                    message = msg  # Your message to send.
                    # Sender ID,While using route4 sender id should be 6
                    # characters long.
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
                    url = "http://api.msg91.com/api/sendhttp.php"  # API URL
                    # URL encoding the data here.
                    postdata = urllib.parse.urlencode(values).encode("utf-8")
                    req = urllib.request.Request(url, postdata)
                    response = urllib.request.urlopen(req)
                    output = response.read()  # Get Response
        else:
            raise Warning("Please enter text")