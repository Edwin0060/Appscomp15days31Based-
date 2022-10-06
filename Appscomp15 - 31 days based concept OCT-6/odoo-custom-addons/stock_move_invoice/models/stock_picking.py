# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Sayooj A O(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    operation_code = fields.Selection(related='picking_type_id.code')
    is_return = fields.Boolean()

    def _compute_invoice_count(self):
        """This compute function used to count the number of invoice for the picking"""
        for picking_id in self:
            move_ids = picking_id.env['account.move'].search([('invoice_origin', '=', picking_id.name)])
            if move_ids:
                self.invoice_count = len(move_ids)
            else:
                self.invoice_count = 0

    def button_validate(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(
                float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(
                float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line
                in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(
                    products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(
                    pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _(
                    '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(
                    pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
                    ', '.join(pickings_without_lots.mapped('name')),
                    ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res
        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        if self.user_has_groups('stock.group_reception_report') \
                and self.user_has_groups('stock.group_auto_reception_report') \
                and self.filtered(lambda p: p.picking_type_id.code != 'outgoing'):
            lines = self.move_lines.filtered(lambda
                                                 m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location']._search(
                    [('id', 'child_of', self.picking_type_id.warehouse_id.view_location_id.id),
                     ('usage', '!=', 'supplier')])
                if self.env['stock.move'].search([
                    ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                    ('product_qty', '>', 0),
                    ('location_id', 'in', wh_location_ids),
                    ('move_orig_ids', '=', False),
                    ('picking_id', 'not in', self.ids),
                    ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = self.action_view_reception_report()
                    action['context'] = {'default_picking_ids': self.ids}
                    return action
        # self.update_sale_price()
        return True

    # def update_sale_price(self):
    #     sale_price_picking = self.env['stock.picking'].search([('sale_id', '=', True)])
    #     prices = []
    #     for unit in sale_price_picking.sale_id.order_line:
    #         vals = (0, 0, {
    #             'price_unit': unit.price_unit
    #         })
    #         prices.append(vals)
    #         print("The price values are", prices)
    #         for price in sale_price_picking.move_ids_without_package:
    #             vals = (0, 0, {
    #                 'price_unit': prices
    #             })
    #         print("Stage 2=======================================", unit.price_unit)

    def create_invoice(self):
        """This is the function for creating customer invoice
        from the picking"""
        global invoice
        for picking_id in self:
            current_user = self.env.uid
            if picking_id.picking_type_id.code == 'outgoing':
                customer_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                    'stock_move_invoice.customer_journal_id') or False
                if not customer_journal_id:
                    raise UserError(_("Alert!, Please configure the journal from settings"))
                invoice_line_list = []
                for move_ids_without_package in picking_id.move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit': move_ids_without_package.price_unit,
                        'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                        else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                        # 'tax_ids': [(6, 0, [picking_id.company_id.account_sale_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    picking_id.create_qty()
                    invoice_line_list.append(vals)
                invoice = picking_id.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': current_user,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.env.user.company_id.currency_id.id,
                    'journal_id': int(customer_journal_id),
                    'payment_reference': picking_id.name,
                    'l10n_in_gst_treatment': 'consumer',
                    'picking_id': picking_id.id,
                    'boutique_id': picking_id.sale_id.id,
                    'invoice_line_ids': invoice_line_list
                })
                sale_sr = self.env['sale.order'].search([('name', '=', self.origin)])
                sale_sr.write({
                    'invoice_id': invoice.id,
                })
                return invoice

    def create_qty(self):
        sale_sr = self.env['sale.order'].search([('name', '=', self.origin)])
        del_obj = self.env['stock.picking'].search([('origin', '=', self.origin), ('state', '=', 'done')])
        added_qty = 0.0
        for line in sale_sr.order_line:
            added_qty = 0.0
            for val in del_obj:
                for qty in val.move_ids_without_package:
                    if qty.product_id.id == line.product_id.id:
                        added_qty += qty.quantity_done
                        product_id = qty.product_id
                if product_id.id == line.product_id.id:
                    line.update({
                        'qty_invoiced': added_qty,
                    })
        return True

    def create_bill(self):
        """This is the function for creating vendor bill
                from the picking"""
        for picking_id in self:
            current_user = self.env.uid
            if picking_id.picking_type_id.code == 'incoming':
                vendor_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                    'stock_move_invoice.vendor_journal_id') or False
                if not vendor_journal_id:
                    raise UserError(_("Please configure the journal from the settings."))
                invoice_line_list = []
                for move_ids_without_package in picking_id.move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit': move_ids_without_package.product_id.lst_price,
                        'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                        else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [picking_id.company_id.account_purchase_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    invoice_line_list.append(vals)
                    invoice = picking_id.env['account.move'].create({
                        'move_type': 'in_invoice',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': current_user,
                        'narration': picking_id.name,
                        'partner_id': picking_id.partner_id.id,
                        'currency_id': picking_id.env.user.company_id.currency_id.id,
                        'journal_id': int(vendor_journal_id),
                        'payment_reference': picking_id.name,
                        'picking_id': picking_id.id,
                        'invoice_line_ids': invoice_line_list
                    })
                    return invoice

    def create_customer_credit(self):
        """This is the function for creating customer credit note
                from the picking"""
        for picking_id in self:
            current_user = picking_id.env.uid
            if picking_id.picking_type_id.code == 'incoming':
                customer_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                    'stock_move_invoice.customer_journal_id') or False
                if not customer_journal_id:
                    raise UserError(_("Please configure the journal from settings"))
                invoice_line_list = []
                for move_ids_without_package in picking_id.move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit': move_ids_without_package.product_id.lst_price,
                        'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                        else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [picking_id.company_id.account_sale_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    invoice_line_list.append(vals)
                    invoice = picking_id.env['account.move'].create({
                        'move_type': 'out_refund',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': current_user,
                        'narration': picking_id.name,
                        'partner_id': picking_id.partner_id.id,
                        'currency_id': picking_id.env.user.company_id.currency_id.id,
                        'journal_id': int(customer_journal_id),
                        'payment_reference': picking_id.name,
                        'picking_id': picking_id.id,
                        'invoice_line_ids': invoice_line_list
                    })
                    return invoice

    def create_vendor_credit(self):
        """This is the function for creating refund
                from the picking"""
        for picking_id in self:
            current_user = self.env.uid
            if picking_id.picking_type_id.code == 'outgoing':
                vendor_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                    'stock_move_invoice.vendor_journal_id') or False
                if not vendor_journal_id:
                    raise UserError(_("Please configure the journal from the settings."))
                invoice_line_list = []
                for move_ids_without_package in picking_id.move_ids_without_package:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit': move_ids_without_package.product_id.lst_price,
                        'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                        else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [picking_id.company_id.account_purchase_tax_id.id])],
                        'quantity': move_ids_without_package.quantity_done,
                    })
                    invoice_line_list.append(vals)
                    invoice = picking_id.env['account.move'].create({
                        'move_type': 'in_refund',
                        'invoice_origin': picking_id.name,
                        'invoice_user_id': current_user,
                        'narration': picking_id.name,
                        'partner_id': picking_id.partner_id.id,
                        'currency_id': picking_id.env.user.company_id.currency_id.id,
                        'journal_id': int(vendor_journal_id),
                        'payment_reference': picking_id.name,
                        'picking_id': picking_id.id,
                        'invoice_line_ids': invoice_line_list
                    })
                    return invoice

    def action_open_picking_invoice(self):
        """This is the function of the smart button which redirect to the
        invoice related to the current picking"""
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('invoice_origin', '=', self.name)],
            'context': {'create': False},
            'target': 'current'
        }


class StockReturnInvoicePicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        """in this function the picking is marked as return"""
        new_picking, pick_type_id = super(StockReturnInvoicePicking, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'is_return': True})
        return new_picking, pick_type_id
