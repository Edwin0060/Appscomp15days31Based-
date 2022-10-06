# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BoutiqueMeasurementFeatures(models.Model):
    _name = 'boutique.measurement.features'
    _description = 'Boutique Measurement Features'

    name = fields.Char(string="Name")


class BoutiqueMeasurement(models.Model):
    _name = 'boutique.measurement'
    _description = 'Boutique Measurement Details'

    name = fields.Char(string="Name")
    sequence = fields.Integer(default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    boutique_feature_id = fields.Many2one('boutique.measurement.features', string='Boutique Feature')
    measurement = fields.Float(string="Measurement")
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    product_id = fields.Many2one('product.template', string='Inventory Relation')
    boutique_product_id = fields.Many2one('boutique.order', string='Product')

    # bill_number = fields.Integer("Bill No")
    # name = fields.Char(string="Name")
    # booking_date = fields.Date(string="Booking Date")
    # delivery_date = fields.Date(string="Delivery Date")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    boutique_id = fields.One2many('boutique.measurement',
                                  'product_id',
                                  string="Boutique Measurement")
    boutique_uom = fields.Many2one('uom.uom', string='Boutique UOM')
    boutique_measurement = fields.Char(string='Boutique Measurement')

    # @api.onchange('boutique_id')
    # def onchange_boutique_id(self):
    #     for val in self:
    #         if val.boutique_id:
    #             val.product_uom = val.boutique_id.uom_id and val.boutique_id.uom_id.id
    #             val.boutique_measurement = val.boutique_id.measurement and val.boutique_id.boutique_id


class BoutiqueDashboard(models.Model):
    _name = "boutique.dashboard.design"
    _description = "Boutique Dashboard Design"

    name = fields.Char(string='Name', default='Nachi Bridal Boutique')
