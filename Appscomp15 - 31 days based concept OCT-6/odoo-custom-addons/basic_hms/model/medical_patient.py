# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from io import BytesIO


class medical_patient(models.Model):
    _name = 'medical.patient'
    _description = 'medical patient'
    _rec_name = 'name'

    @api.onchange('patient_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.patient_id
        self.partner_address_id = address_id

    def print_report(self):
        return self.env.ref('basic_hms.report_print_patient_card').report_action(self)

    @api.depends('date_of_birth')
    def onchange_age(self):
        for rec in self:
            if rec.date_of_birth:
                d1 = rec.date_of_birth
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.age = str(rd.years) + "y" + " " + str(rd.months) + "m" + " " + str(rd.days) + "d"
            else:
                rec.age = "No Date Of Birth!!"

    patient_id = fields.Many2one('res.partner', domain=[('is_patient', '=', True)], string="Patient", required=False)
    name = fields.Char(string='ID', readonly=True)
    last_name = fields.Char('Last Name')
    date_of_birth = fields.Date(string="Date of Birth")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
    age = fields.Char(compute=onchange_age, string="Patient Age", store=True)
    critical_info = fields.Text(string="Patient Critical Information")
    photo = fields.Binary(string="Picture")
    blood_type = fields.Selection([('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'),
                                   ('AB+', 'AB+'), ('AB-', 'AB- ')], string="Blood Type")
    rh = fields.Selection([('-+', '+'), ('--', '-')], string="Rh")
    marital_status = fields.Selection(
        [('s', 'Single'), ('m', 'Married'), ('w', 'Widowed'), ('d', 'Divorced'), ('x', 'Seperated')],
        string='Marital Status')
    deceased = fields.Boolean(string='Deceased')
    date_of_death = fields.Date(string="Date of Death")
    cause_of_death = fields.Char(string='Cause of Death')
    receivable = fields.Float(string="Receivable", readonly=True)
    current_insurance_id = fields.Many2one('medical.insurance', string="Insurance")
    partner_address_id = fields.Many2one('res.partner', string="Address", )

    primary_care_physician_id = fields.Many2one('medical.physician', string="Primary Care Doctor")
    patient_status = fields.Char(string="Hospitalization Status", readonly=True)
    patient_disease_ids = fields.One2many('medical.patient.disease', 'patient_id')
    patient_psc_ids = fields.One2many('medical.patient.psc', 'patient_id')
    excercise = fields.Boolean(string='Exercise')
    excercise_minutes_day = fields.Integer(string="Minutes/Day")
    sleep_hours = fields.Integer(string="Hours of sleep")
    sleep_during_daytime = fields.Boolean(string="Sleep at daytime")
    number_of_meals = fields.Integer(string="Meals per day")
    coffee = fields.Boolean('Coffee')
    coffee_cups = fields.Integer(string='Cups Per Day')
    eats_alone = fields.Boolean(string="Eats alone")
    soft_drinks = fields.Boolean(string="Soft drinks(sugar)")
    salt = fields.Boolean(string="Salt")
    diet = fields.Boolean(string=" Currently on a diet ")
    diet_info = fields.Integer(string=' Diet info ')
    general_info = fields.Text(string="Info")
    lifestyle_info = fields.Text('Lifestyle Information')
    smoking = fields.Boolean(string="Smokes")
    smoking_number = fields.Integer(string="Cigarretes a day")
    ex_smoker = fields.Boolean(string="Ex-smoker")
    second_hand_smoker = fields.Boolean(string="Passive smoker")
    age_start_smoking = fields.Integer(string="Age started to smoke")
    age_quit_smoking = fields.Integer(string="Age of quitting")
    drug_usage = fields.Boolean(string='Drug Habits')
    drug_iv = fields.Boolean(string='IV drug user')
    ex_drug_addict = fields.Boolean(string='Ex drug addict')
    age_start_drugs = fields.Integer(string='Age started drugs')
    age_quit_drugs = fields.Integer(string="Age quit drugs")
    alcohol = fields.Boolean(string="Drinks Alcohol")
    ex_alcohol = fields.Boolean(string="Ex alcoholic")
    age_start_drinking = fields.Integer(string="Age started to drink")
    age_quit_drinking = fields.Integer(string="Age quit drinking")
    alcohol_beer_number = fields.Integer(string="Beer / day")
    alcohol_wine_number = fields.Integer(string="Wine / day")
    alcohol_liquor_number = fields.Integer(string="Liquor / day")
    cage_ids = fields.One2many('medical.patient.cage', 'patient_id')
    sex_oral = fields.Selection([('0', 'None'),
                                 ('1', 'Active'),
                                 ('2', 'Passive'),
                                 ('3', 'Both')], string='Oral Sex')
    sex_anal = fields.Selection([('0', 'None'),
                                 ('1', 'Active'),
                                 ('2', 'Passive'),
                                 ('3', 'Both')], string='Anal Sex')
    prostitute = fields.Boolean(string='Prostitute')
    sex_with_prostitutes = fields.Boolean(string=' Sex with prostitutes ')
    sexual_preferences = fields.Selection([
        ('h', 'Heterosexual'),
        ('g', 'Homosexual'),
        ('b', 'Bisexual'),
        ('t', 'Transexual'),
    ], 'Sexual Orientation', sort=False)
    sexual_practices = fields.Selection([
        ('s', 'Safe / Protected sex'),
        ('r', 'Risky / Unprotected sex'),
    ], 'Sexual Practices', sort=False)
    sexual_partners = fields.Selection([
        ('m', 'Monogamous'),
        ('t', 'Polygamous'),
    ], 'Sexual Partners', sort=False)
    sexual_partners_number = fields.Integer('Number of sexual partners')
    first_sexual_encounter = fields.Integer('Age first sexual encounter')
    anticonceptive = fields.Selection([
        ('0', 'None'),
        ('1', 'Pill / Minipill'),
        ('2', 'Male condom'),
        ('3', 'Vasectomy'),
        ('4', 'Female sterilisation'),
        ('5', 'Intra-uterine device'),
        ('6', 'Withdrawal method'),
        ('7', 'Fertility cycle awareness'),
        ('8', 'Contraceptive injection'),
        ('9', 'Skin Patch'),
        ('10', 'Female condom'),
    ], 'Anticonceptive Method', sort=False)
    sexuality_info = fields.Text('Extra Information')
    motorcycle_rider = fields.Boolean('Motorcycle Rider', help="The patient rides motorcycles")
    helmet = fields.Boolean('Uses helmet', help="The patient uses the proper motorcycle helmet")
    traffic_laws = fields.Boolean('Obeys Traffic Laws', help="Check if the patient is a safe driver")
    car_revision = fields.Boolean('Car Revision', help="Maintain the vehicle. Do periodical checks - tires,breaks ...")
    car_seat_belt = fields.Boolean('Seat belt', help="Safety measures when driving : safety belt")
    car_child_safety = fields.Boolean('Car Child Safety',
                                      help="Safety measures when driving : child seats, proper seat belting, "
                                           "not seating on the front seat, ....")
    home_safety = fields.Boolean('Home safety',
                                 help="Keep safety measures for kids in the kitchen, correct storage of chemicals, ...")
    fertile = fields.Boolean('Fertile')
    menarche = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    menopause = fields.Integer('Menopause age')
    menstrual_history_ids = fields.One2many('medical.patient.menstrual.history', 'patient_id')
    breast_self_examination = fields.Boolean('Breast self-examination')
    mammography = fields.Boolean('Mammography')
    pap_test = fields.Boolean('PAP test')
    last_pap_test = fields.Date('Last PAP test')
    colposcopy = fields.Boolean('Colposcopy')
    mammography_history_ids = fields.One2many('medical.patient.mammography.history', 'patient_id')
    pap_history_ids = fields.One2many('medical.patient.pap.history', 'patient_id')
    colposcopy_history_ids = fields.One2many('medical.patient.colposcopy.history', 'patient_id')
    pregnancies = fields.Integer('Pregnancies')
    premature = fields.Integer('Premature')
    stillbirths = fields.Integer('Stillbirths')
    abortions = fields.Integer('Abortions')
    pregnancy_history_ids = fields.One2many('medical.patient.pregnency', 'patient_id')
    family_history_ids = fields.Many2many('medical.family.disease', string="Family Disease Lines")
    perinatal_ids = fields.Many2many('medical.preinatal')
    ex_alcoholic = fields.Boolean('Ex alcoholic')
    currently_pregnant = fields.Boolean('Currently Pregnant')
    born_alive = fields.Integer('Born Alive')
    gpa = fields.Char('GPA')
    works_at_home = fields.Boolean('Works At Home')
    colposcopy_last = fields.Date('Last colposcopy')
    mammography_last = fields.Date('Last mammography')
    ses = fields.Selection([
        ('None', ''),
        ('0', 'Lower'),
        ('1', 'Lower-middle'),
        ('2', 'Middle'),
        ('3', 'Middle-upper'),
        ('4', 'Higher'),
    ], 'Socioeconomics', help="SES - Socioeconomic Status", sort=False)
    education = fields.Selection([('o', 'None'), ('1', 'Incomplete Primary School'),
                                  ('2', 'Primary School'),
                                  ('3', 'Incomplete Secondary School'),
                                  ('4', 'Secondary School'),
                                  ('5', 'University')], string='Education Level')
    housing = fields.Selection([
        ('None', ''),
        ('0', 'Shanty, deficient sanitary conditions'),
        ('1', 'Small, crowded but with good sanitary conditions'),
        ('2', 'Comfortable and good sanitary conditions'),
        ('3', 'Roomy and excellent sanitary conditions'),
        ('4', 'Luxury and excellent sanitary conditions'),
    ], 'Housing conditions', help="Housing and sanitary living conditions", sort=False)
    works = fields.Boolean('Works')
    hours_outside = fields.Integer('Hours outside home',
                                   help="Number of hours a day the patient spend outside the house")
    hostile_area = fields.Boolean('Hostile Area')
    notes = fields.Text(string="Extra info")
    sewers = fields.Boolean('Sanitary Sewers')
    water = fields.Boolean('Running Water')
    trash = fields.Boolean('Trash recollection')
    electricity = fields.Boolean('Electrical supply')
    gas = fields.Boolean('Gas supply')
    telephone = fields.Boolean('Telephone')
    television = fields.Boolean('Television')
    internet = fields.Boolean('Internet')
    single_parent = fields.Boolean('Single parent family')
    domestic_violence = fields.Boolean('Domestic violence')
    working_children = fields.Boolean('Working children')
    teenage_pregnancy = fields.Boolean('Teenage pregnancy')
    sexual_abuse = fields.Boolean('Sexual abuse')
    drug_addiction = fields.Boolean('Drug addiction')
    school_withdrawal = fields.Boolean('School withdrawal')
    prison_past = fields.Boolean('Has been in prison')
    prison_current = fields.Boolean('Is currently in prison')
    relative_in_prison = fields.Boolean('Relative in prison',
                                        help="Check if someone from the nuclear family - parents sibblings  is or has been in prison")
    fam_apgar_help = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Help from family',
        help="Is the patient satisfied with the level of help coming from the family when there is a problem ?",
        sort=False)
    fam_apgar_discussion = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Problems discussion',
        help="Is the patient satisfied with the level talking over the problems as family ?", sort=False)
    fam_apgar_decisions = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Decision making',
        help="Is the patient satisfied with the level of making important decisions as a group ?", sort=False)
    fam_apgar_timesharing = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Time sharing',
        help="Is the patient satisfied with the level of time that they spend together ?", sort=False)
    fam_apgar_affection = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Family affection',
        help="Is the patient satisfied with the level of affection coming from the family ?", sort=False)
    fam_apgar_score = fields.Integer('Score',
                                     help="Total Family APGAR 7 - 10 : Functional Family 4 - 6  : Some level of disfunction \n"
                                          "0 - 3  : Severe disfunctional family \n")
    lab_test_ids = fields.One2many('medical.patient.lab.test', 'patient_id')
    fertile = fields.Boolean('Fertile')
    menarche_age = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    pap_test_last = fields.Date('Last PAP Test')
    colposcopy = fields.Boolean('Colpscopy')
    gravida = fields.Integer('Pregnancies')
    medical_vaccination_ids = fields.One2many('medical.vaccination', 'medical_patient_vaccines_id')
    medical_appointments_ids = fields.One2many('medical.appointment', 'patient_id', string='Appointments')
    lastname = fields.Char('Last Name')
    report_date = fields.Date('Date', default=datetime.today().date())
    medication_ids = fields.One2many('medical.patient.medication1', 'medical_patient_medication_id')
    deaths_2nd_week = fields.Integer('Deceased after 2nd week')
    deaths_1st_week = fields.Integer('Deceased after 1st week')
    full_term = fields.Integer('Full Term')
    ses_notes = fields.Text('Notes')

    qr_code = fields.Binary('QRcode', compute="_generate_qr")
    qr_code_content = fields.Text(string='QR Content', compute='get_qr_code_content')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('register', 'Registered'),
        ('visit', 'Visited'),
        ('prescription', 'Prescription'),
        ('lab', 'Lab'),
        ('physician', 'Physician'),
        ('pharmacy', 'Pharmacy'),
        ('invoice', 'Invoiced'),
        ('paid', 'Paid'),
    ], 'State', default='draft')
    registered_date = fields.Datetime(string='Registered Date')
    patient_category = fields.Selection([('new', 'New Patient'), ('exist', 'Re-Visit')], string='Patient Category',
                                        default='new')
    patient_name = fields.Char(string="Patient")
    mobile_number = fields.Char(string='Mobile Number')
    patient_email = fields.Char(string='Email')

    # Address fields
    street = fields.Char('Street', readonly=False, store=True)
    street2 = fields.Char('Street2', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, readonly=False, store=True)
    city = fields.Char('City', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        readonly=False, store=True)
    medical_patient_id = fields.Many2one('medical.patient', string='MRD Number',
                                         domain="[('mobile_number', '=', mobile_number_search)]")

    mobile_number_search = fields.Char(string='Mobile Number')
    token_number = fields.Char(string='Token Number')
    today_date = fields.Date(string='Date', default=fields.Date.today())

    doctor_image = fields.Binary('Doctor')
    patient_history_count = fields.Integer(string="History", copy=False,
                                           compute='get_patient_history_count')

    patient_admit = fields.Boolean(string='Patient Admit')
    patient_lab = fields.Boolean(string='Patient Lab')
    patient_xray = fields.Boolean(string='Patient X-Ray')
    patient_physio = fields.Boolean(string='Patient Physio')

    patient_admit_close = fields.Boolean(string='Patient Admit Close')
    patient_lab_close = fields.Boolean(string='Patient Lab Close')
    patient_xray_close = fields.Boolean(string='Patient X-Ray Close')
    patient_physio_close = fields.Boolean(string='Patient Physio Close')

    admission_type = fields.Selection(
        [('routine', 'Routine'), ('maternity', 'Maternity'), ('elective', 'Elective'), ('urgent', 'Urgent'),
         ('emergency', 'Emergency  ')], string="Admission Type")
    medical_test_type_id = fields.Many2one('medical.test_type', 'Test Type')


    def open_fitness_report_form(self):
        action = self.env.ref('basic_hms.open_fitness_action_report')
        result = action.read()[0]
        result['context'] = {
            'default_name': self.patient_name,
            'default_patient_age': self.age,
            'default_patient_gender': dict(self._fields['sex'].selection).get(self.sex),
            'default_patient_image': self.photo,
            'default_doctor': self.primary_care_physician_id.partner_id.name,

        }
        return result


    def create_admit_details(self):
        admit = self.env['medical.inpatient.registration']
        admit.create({
            'patient_id': self.id,
            'hospitalization_date': fields.Datetime.now(),
            'admission_type': self.admission_type,
        })
        self.write({
            'name': self.name + '(IP)',
            'patient_admit_close': True,
        })


    def create_lab_details(self):
        admit = self.env['medical.patient.lab.test']
        test_type = self.env['medical.test_type'].search([('name', '=', 'XRay')])
        admit.create({
            'medical_test_type_id': self.medical_test_type_id.id,
            'patient_id': self.id,
            'doctor_id': self.primary_care_physician_id.id,
        })
        self.write({
            'patient_lab_close': True,
        })


    def create_xray_details(self):
        print('-----------------------------')
        self.write({
            'patient_xray_close': True,
        })

    def create_physio_details(self):
        print('-----------------------------')
        self.write({
            'patient_physio_close': True,
        })

    @api.onchange('primary_care_physician_id')
    def _onchange_primary_care_physician_id(self):
        self.write({
            'doctor_image': self.primary_care_physician_id.partner_id.image_1920,
            'receivable': self.primary_care_physician_id.op_visit_charge,
        })

    def get_patient_history_count(self):
        self.patient_history_count = self.env['medical.patient'].sudo().search_count(
            [('mobile_number', '=', self.mobile_number_search), ('id', '!=', self.id)])

    def get_patient_history(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('basic_hms.medical_patients_form_view')
        tree_view = self.sudo().env.ref('basic_hms.medical_patients_tree_view')
        return {
            'name': _('Patient History'),
            'res_model': 'medical.patient',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('mobile_number', '=', self.mobile_number_search), ('id', '!=', self.id)],
        }

    @api.onchange('medical_patient_id')
    def _onchange_medical_patient_id(self):
        self.write({
            'patient_email': self.medical_patient_id.patient_email,
            'street': self.medical_patient_id.street,
            'street2': self.medical_patient_id.street2,
            'city': self.medical_patient_id.city,
            'state_id': self.medical_patient_id.state_id.id,
            'zip': self.medical_patient_id.zip,
            'country_id': self.medical_patient_id.country_id.id,
            'sex': self.medical_patient_id.sex,
            'date_of_birth': self.medical_patient_id.date_of_birth,
            'primary_care_physician_id': self.medical_patient_id.primary_care_physician_id.id,
            'marital_status': self.medical_patient_id.marital_status,
            'age': self.medical_patient_id.age,
        })

    @api.onchange('mobile_number_search')
    def _onchange_mobile_number_search(self):
        if self.mobile_number_search:
            partner_id = self.env['res.partner'].search([('mobile', '=', self.mobile_number_search)])
            self.write({
                'patient_id': partner_id.id,
                'patient_name': partner_id.name,
            })

    def create_res_partner_details(self):
        if self.patient_category == 'new':
            res_partner_obj = self.env['res.partner']
            res_partner_obj.create({
                'name': self.patient_name,
                'mobile': self.mobile_number,
                'email': self.patient_email,
                'street': self.street,
                'street2': self.street2,
                'city': self.city,
                'state_id': self.state_id.id,
                'zip': self.zip,
                'country_id': self.country_id.id,
            })

    def set_register(self):
        self.write({
            'registered_date': fields.Datetime.now(),
            'state': 'register',
        })

    def set_visited(self):
        self.write({
            # 'registered_date': fields.Datetime.now(),
            'state': 'visit',
        })

    def get_qr_code_content(self):
        if self.mobile_number:
            patient_mobile = self.mobile_number
        if not self.mobile_number:
            patient_mobile = "Nil"
        if not self.sex:
            sex = 'NIl'
        else:
            if self.sex == 'm':
                sex = 'Male'
            elif self.sex == 'f':
                sex = 'FeMale'
        problem = ','.join([str(partner) for partner in
                            self.patient_disease_ids.pathology_id.mapped('name')])
        if not problem:
            problem = "Nil"
        self.qr_code_content = 'ID : ' + self.name + '\n Patient Name : ' + \
                               self.patient_name + '\n Mobile Number : ' + patient_mobile + '\n Age : ' + \
                               self.age + '\n Gender : ' + sex + '\n Disease : ' + problem

    def _generate_qr(self):
        "method to generate QR code"
        for rec in self:
            if qrcode and base64:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=4,
                )
                # qr.add_data("ID : ")
                qr.add_data(rec.qr_code_content)
                # qr.add_data(", Name : ")
                # qr.add_data(rec.patient_id.name)
                # qr.add_data(", Mobile : ")
                # qr.add_data(rec.patient_id.mobile)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                rec.update({'qr_code': qr_image})
            else:
                raise UserError(_('Necessary Requirements To Run This Operation Is Not Satisfied'))

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create(self, val):
        appointment = self._context.get('appointment_id')
        res_partner_obj = self.env['res.partner']
        if appointment:
            val_1 = {'name': self.env['res.partner'].browse(val['patient_id']).name}
            patient = res_partner_obj.create(val_1)
            val.update({'patient_id': patient.id})
        if val.get('date_of_birth'):
            dt = val.get('date_of_birth')
            d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
            d2 = datetime.today().date()
            rd = relativedelta(d2, d1)
            age = str(rd.years) + "y" + " " + str(rd.months) + "m" + " " + str(rd.days) + "d"
            val.update({'age': age})
        val['name'] = self.env['ir.sequence'].next_by_code('medical.patient') or 'New'
        val['token_number'] = self.env['ir.sequence'].next_by_code('medical.patient.token')
        result = super(medical_patient, self).create(val)
        result.create_res_partner_details()
        return result

    @api.constrains('date_of_death')
    def _check_date_death(self):
        for rec in self:
            if rec.date_of_birth:
                if rec.deceased == True:
                    if rec.date_of_death <= rec.date_of_birth:
                        raise UserError(_('Date Of Death Can Not Less Than Date Of Birth.'))

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate Patient.'))

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
