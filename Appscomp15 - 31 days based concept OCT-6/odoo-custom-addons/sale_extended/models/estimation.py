from odoo import models, fields, api, tools, _
import time
import odoo.addons.decimal_precision as dp


class SaleEstimation(models.Model):
    '''Defines an sale estimation '''

    _name = "sale.estimation"
    _description = "Sale Estimation"
    _order = "name"

    name = fields.Char(string='Indent Reference', size=256, tracking=True, required=True, copy=False, index=True,
                       default=lambda self: _('/'),
                       help='Sequence order you want to see this sale estimation.')
    # code = fields.Char('Code', required=True, help='Code of academic year')
    # current = fields.Boolean('Current', help="Set Active Current Year")
    description = fields.Text('Description')
    product_id = fields.Many2one('product.product', string='Product')
    state = fields.Selection([('draft', 'Draft'), ('cancel', 'Cancelled'),
                              ('confirm', 'Confimred'),
                              ('reject', 'Rejected')], 'State', default="draft", readonly=True, tracking=True)
    estimation_detailed_type = fields.Selection([
        ('cons', 'Consumable'), ('service', 'Services'),
        ('product', 'Storable Product'),
    ], 'Product Type')
    estimated_cate_id = fields.Many2one("product.category", string="Product Category")
    estimation_pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    estimation_attribute_id = fields.Many2one('product.attribute', string='Estimation Product Attributes')
    product_qty = fields.Float("Product Quantity")
    product_price = fields.Float("Product Price")
    product_unit_subtotal = fields.Float("Subtotal")
    # total = fields.Float("Total")
    total = fields.Monetary(currency_field='currency_field',string="Total")
    sub_total = fields.Float("Sub Total")
    estimation_tax = fields.Selection([
        ('inc_tax', 'Inclusive Tax'), ('exc', 'Exclusive Tax')
    ], 'Tax Type', default='exc')
    inclusive_tax_amount = fields.Float(string='Inclusive Tax')
    currency_field = fields.Many2one("res.currency", string="Currency")
    product_lines = fields.One2many('sale.estimation.product.line', 'estimate_id', 'Products')
    estimation_tax_id = fields.Many2many('account.tax', string='Tax')
    taxes = fields.One2many('sale.estimation.tax', 'sale_estimation_order', string='Taxes',
                            compute='_compute_purchase_order_taxes',store=True)
    estimation_tax_value = fields.Float(string="Tax Value")
    date = fields.Datetime('Estimation Date', required=True,
                           default=lambda self: fields.Datetime.now())
    estimation_date = fields.Datetime('Estimation Dates New', readonly=True,)
    # total_tax = fields.Float(string="Tax")
    total_tax = fields.Monetary(currency_field='currency_field', string="Tax")
    partner_name = fields.Many2one('res.partner', string=' Customer' , required=True)
    note = fields.Text(string="Terms and Conditions :")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


    #
    # def _onchangestimatione_date_format(self):
    #     for record in self:
    #         ref_date1 = record.date
    #         import datetime
    #         d11 = str(ref_date1)
    #         dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d')
    #         date1 = dt21.strftime("%d/%m/%Y")
    #         record.estimation_date = date1




    @api.onchange("product_id")
    def get_product_tax_value(self):
        for record in self:
            if record.estimation_tax == 'exc':
                if record.product_id.taxes_id:
                    record.estimation_tax_id = record.product_id.taxes_id.ids
            else:
                record.estimation_tax_id = False

    @api.onchange("product_id", "estimation_pricelist_id.item_ids")
    def get_product_details(self):
        for record in self:
            for pricelist in record.estimation_pricelist_id.item_ids:
                if pricelist.product_id.display_name == record.product_id.display_name:
                    record.product_qty = pricelist.min_quantity
                    record.product_price = pricelist.fixed_price

    @api.onchange("product_qty", "product_price")
    def get_estimation_subtotal(self):
        for rec in self:
            subtotal = 0.00
            if rec.product_qty and rec.product_price > 0.00:
                subtotal = rec.product_qty * rec.product_price
                rec.product_unit_subtotal = subtotal

    @api.onchange("estimation_tax_value")
    def get_tax_subtotal(self):
        for rec in self:
            if rec.estimation_tax == 'exc':
                taxsubtotal = 0.00
                if rec.estimation_tax_value > 0.00:
                    taxsubtotal += rec.estimation_tax_value
                rec.total_tax = taxsubtotal

    def get_line_products_details(self):
        for record in self:
            total = 0.00
            for final_total in record.product_lines:
                total += final_total.prod_subtotal
            record.total = total +  record.total_tax

    def get_line_items(self):
        line_vals = []
        for line in self:
            if line.product_qty and line.product_price:
                vals = [0, 0, {
                    'products_id': line.product_id.id,
                    'prod_qty': line.product_qty,
                    'prod_price': line.product_price,
                    'prod_subtotal': line.product_unit_subtotal,
                    # 'prod_subtotal': line.product_unit_subtotal + line.estimation_tax_value,
                }]
                line_vals.append(vals)
        return line_vals

    def button_product_update(self):
        product_updation = False
        for line in self:
            if line.product_qty and line.product_price:
                product_updation = line.update({
                    'product_id': False,
                    'product_qty': False,
                    'product_price': False,
                    'estimation_tax_id': False,
                    'product_unit_subtotal': False,
                    'product_lines': line.get_line_items(),
                })
            self.get_line_products_details()
            return True

    @api.depends('estimation_tax_id', 'product_qty')
    def _compute_purchase_order_taxes(self):
        for rec in self:
            rec.taxes = [(5, 0, 0)]
            for line in rec:
                previous_taxes_ids = rec.taxes.mapped('tax_id').ids
                if line.estimation_tax_id:
                    price = line.product_price
                    taxes = line.estimation_tax_id.compute_all(
                        price, line.currency_field, line.product_qty, product=line.product_id,
                    )['taxes']
                    val_list = []
                    for tax in taxes:
                        if tax['id'] in previous_taxes_ids:
                            purchase_tax = rec.taxes.filtered(lambda taxes: taxes.tax_id.id == tax['id'])
                            purchase_tax.amount += tax['amount']
                        else:
                            val = {
                                'sale_estimation_order': rec.id,
                                'name': tax['name'],
                                'tax_id': tax['id'],
                                'amount': tax['amount'],
                                'account_id': tax['account_id'],
                            }
                            val_list.append(val)
                    rec.taxes.create(val_list)

    @api.onchange("taxes")
    def get_product_estimation_tax_value(self):
        for record in self:
            final_tax = 0.00
            for tax in record.taxes:
                final_tax += tax.amount
            record.estimation_tax_value = final_tax
            # if record.estimation_tax == "inc_tax":
            #    print("")

    def sale_estimation_confirm(self):
        for record in self:
            record.write({'state': 'confirm'})

    @api.model
    def create(self, values):
        values['name'] = self.sudo().env['ir.sequence'].get('sale.estimation') or '/'
        res = super(SaleEstimation, self).create(values)
        return res


class SaleEstimationProductLine(models.Model):
    '''Defines an sale estimation '''

    _name = "sale.estimation.product.line"
    _description = "Sale Estimation Line"

    estimate_id = fields.Many2one('sale.estimation', 'Sale Estimation', required=True)
    # products_id = fields.Many2one('product.template',"Products")
    products_id = fields.Many2one('product.product', "Products")
    prod_qty = fields.Float("Product Quantity")
    prod_price = fields.Float("Product Price")
    prod_subtotal = fields.Float("Subtotal")


class SaleEstimtationTax(models.Model):
    _name = 'sale.estimation.tax'
    _description = 'Sale Estimation Tax'

    sale_estimation_order = fields.Many2one('sale.estimation', string='Sale Estimation Order', ondelete='cascade')
    name = fields.Char(string='Tax Description', required=True)
    amount = fields.Float(string='Amount')
    account_id = fields.Many2one('account.account', string='Tax Account')
    tax_id = fields.Many2one('account.tax', string="Tax")

#
