# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # def button_validate(self):
    #     # Clean-up the context key at validation to avoid forcing the creation of immediate
    #     # transfers.
    #     ctx = dict(self.env.context)
    #     ctx.pop('default_immediate_transfer', None)
    #     self = self.with_context(ctx)
    #
    #     # Sanity checks.
    #     pickings_without_moves = self.browse()
    #     pickings_without_quantities = self.browse()
    #     pickings_without_lots = self.browse()
    #     products_without_lots = self.env['product.product']
    #     for picking in self:
    #         if not picking.move_lines and not picking.move_line_ids:
    #             pickings_without_moves |= picking
    #
    #         picking.message_subscribe([self.env.user.partner_id.id])
    #         picking_type = picking.picking_type_id
    #         precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #         no_quantities_done = all(
    #             float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
    #             picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
    #         no_reserved_quantities = all(
    #             float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line
    #             in picking.move_line_ids)
    #         if no_reserved_quantities and no_quantities_done:
    #             pickings_without_quantities |= picking
    #
    #         if picking_type.use_create_lots or picking_type.use_existing_lots:
    #             lines_to_check = picking.move_line_ids
    #             if not no_quantities_done:
    #                 lines_to_check = lines_to_check.filtered(
    #                     lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
    #             for line in lines_to_check:
    #                 product = line.product_id
    #                 if product and product.tracking != 'none':
    #                     if not line.lot_name and not line.lot_id:
    #                         pickings_without_lots |= picking
    #                         products_without_lots |= product
    #
    #     if not self._should_show_transfers():
    #         if pickings_without_moves:
    #             raise UserError(_('Please add some items to move.'))
    #         if pickings_without_quantities:
    #             raise UserError(self._get_without_quantities_error_message())
    #         if pickings_without_lots:
    #             raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(
    #                 products_without_lots.mapped('display_name')))
    #     else:
    #         message = ""
    #         if pickings_without_moves:
    #             message += _('Transfers %s: Please add some items to move.') % ', '.join(
    #                 pickings_without_moves.mapped('name'))
    #         if pickings_without_quantities:
    #             message += _(
    #                 '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(
    #                 pickings_without_quantities.mapped('name'))
    #         if pickings_without_lots:
    #             message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
    #                 ', '.join(pickings_without_lots.mapped('name')),
    #                 ', '.join(products_without_lots.mapped('display_name')))
    #         if message:
    #             raise UserError(message.lstrip())
    #
    #     # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
    #     # moves and/or the context and never call `_action_done`.
    #     if not self.env.context.get('button_validate_picking_ids'):
    #         self = self.with_context(button_validate_picking_ids=self.ids)
    #     res = self._pre_action_done_hook()
    #     if res is not True:
    #         return res
    #     # Call `_action_done`.
    #     if self.env.context.get('picking_ids_not_to_backorder'):
    #         pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
    #         pickings_to_backorder = self - pickings_not_to_backorder
    #     else:
    #         pickings_not_to_backorder = self.env['stock.picking']
    #         pickings_to_backorder = self
    #     pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
    #     pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
    #
    #     if self.user_has_groups('stock.group_reception_report') \
    #             and self.user_has_groups('stock.group_auto_reception_report') \
    #             and self.filtered(lambda p: p.picking_type_id.code != 'outgoing'):
    #         lines = self.move_lines.filtered(lambda
    #                                              m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
    #         if lines:
    #             # don't show reception report if all already assigned/nothing to assign
    #             wh_location_ids = self.env['stock.location']._search(
    #                 [('id', 'child_of', self.picking_type_id.warehouse_id.view_location_id.id),
    #                  ('usage', '!=', 'supplier')])
    #             if self.env['stock.move'].search([
    #                 ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
    #                 ('product_qty', '>', 0),
    #                 ('location_id', 'in', wh_location_ids),
    #                 ('move_orig_ids', '=', False),
    #                 ('picking_id', 'not in', self.ids),
    #                 ('product_id', 'in', lines.product_id.ids)], limit=1):
    #                 action = self.action_view_reception_report()
    #                 action['context'] = {'default_picking_ids': self.ids}
    #                 return action
    #     # self.update_sale_price()
    #     return True

    # def update_sale_price(self):
    #     sale_price_picking = self.env['stock.picking'].search([('id', '=', self.id), ('state', '=', 'done')])
    #     print("The sale_price_picking---------------------------------------------------",
    #           sale_price_picking.sale_id.name)
    #     for price in sale_price_picking.sale_id.order_line:
    #         print("Stage 2=======================================", price.price_unit)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    boutique_id = fields.Many2one('sale.order', string='Reference')


class AccountMove(models.Model):
    _inherit = "account.move"

    boutique_id = fields.Many2one('sale.order', string='Reference')
    sale_advance_amount = fields.Float(string='Sale Advance', related='picking_id.sale_id.advanced_payment')

    def action_post(self):
        for val in self:
            if not val.invoice_line_ids:
                raise ValidationError('Alert!!, Mr.%s, Please Add Products in the %s - Boutique Invoice Line to '
                                      'Confirm '
                                      'the Order.' % (self.env.user.name, self.name))
            if val.invoice_line_ids:
                for price in val.invoice_line_ids:
                    if price.price_unit == 0.00:
                        raise ValidationError(
                            'Alert!!, Mr.%s,  Add the %s - Boutique Invoice Line Products Unit Price and Confirm the '
                            'Order.' % (self.env.user.name, self.name))
            # val.boutique_id.write({
            #     'balance_payment': val.amount_residual
            # })
        return super(AccountMove, self).action_post()

#
# class SaleAdvancePaymentInv(models.TransientModel):
#     _inherit = "sale.advance.payment.inv"
#     _description = "Sales Advance Payment Invoice"
#
#     def create_invoices(self):
#         invoice_vals = {
#             'boutique_id': self.id,
#         }
#         invoice = self.env['account.move'].sudo().create(invoice_vals)
#         print('--------------------SUCCES----------------')
#         return super(SaleAdvancePaymentInv, self).create_invoices()
