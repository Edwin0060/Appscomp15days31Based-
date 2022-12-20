from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class DirectDeliveryIndent(models.Model):
    _name = 'direct.delivery.indent'
    _description = 'Direct Delivery Indent'

    def _get_stock_type_ids(self):
        data = self.env['stock.picking.type'].search([])
        for line in data:
            if line.code == 'outgoing':
                return line

    def _default_employee(self):
        emp_ids = self.sudo().env['hr.employee'].search([('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    name = fields.Char(string='Name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('delivered_create', 'Delivered Created'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancelled'),
    ], default='draft')
    # direct_delivery_request_type = fields.Selection([
    #     ('user', 'Direct Store Team'),
    #     ('employee', 'Request For Employee'),
    # ], default='user')
    delivery_responsible = fields.Many2one('hr.employee', string='Request Raised By', default=_default_employee,
                                           help="Responsible person for the Direct Delivery Request")
    department_id = fields.Many2one(string='Department', related='delivery_responsible.department_id', tracking=True)
    current_job_id = fields.Many2one(related='delivery_responsible.job_id', string="Job Position")
    current_reporting_manager = fields.Many2one('hr.employee', string="Reporting Manager")
    delivery_request_raised_for = fields.Many2one('hr.employee', string='Request Raised For',
                                                  help="Request person for the Direct Delivery")
    requester_department_id = fields.Many2one('hr.department', string='Department',
                                              related='delivery_request_raised_for.department_id',
                                              tracking=True)
    requester_current_job_id = fields.Many2one('hr.job', string="Job Position",
                                               related='delivery_request_raised_for.job_id')
    requester_current_reporting_manager = fields.Many2one('hr.employee', string="Responsible Nurse")
    delivery_type = fields.Selection([
        ('internal', 'Pharmacy'),
        ('external', 'Operation Theatre'),
    ], string='Request Raised For')
    # ho_department = fields.Many2one('ho.department', string='Department')
    purpose = fields.Char('Purpose', tracking=True)
    move_type = fields.Selection([('direct', 'Partial'), ('one', 'All at once')], 'Receive Method',
                                 help="It specifies goods to be deliver partially or all at once")
    picking_type_id = fields.Many2one('stock.picking.type', 'Warehouse', default=_get_stock_type_ids,
                                      help="This will determine picking type of incoming shipment")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', help="default warehouse where inward will be taken")
    approved_by = fields.Many2one('res.users', string='Approved By')
    verified_date = fields.Datetime('Verified Date', readonly=True, tracking=True)
    po_approved_by = fields.Char('PO Approved By')
    issued_date = fields.Datetime('Issued Date')
    inward_date = fields.Datetime('Inward Date')
    store_incharge = fields.Char('Store In-charge')
    stock_picking_id = fields.Many2one('stock.picking', string="Picking Id", copy=False)
    direct_delivery_backorder_count = fields.Integer(compute='_compute_direct_delivery_backorder',
                                                     string='Back Order',
                                                     default=0)
    direct_delivery_picking_count = fields.Integer(compute='_compute_direct_delivery_picking',
                                                   string='Picking',
                                                   default=0)

    delivery_product_lines = fields.One2many('direct.delivery.indent.line', 'direct_indent_id', 'Products',
                                             readonly=True)
    origin = fields.Char(string='Source Document')

    def set_submit(self):
        if self.delivery_product_lines:
            for line_id in self.delivery_product_lines:
                if line_id.product_available == 0.00:
                    raise UserError(_("Alert!, Hi %s,The selected Products On-Hand Qty is zero,Please check it."
                                      % self.env.user.name))
        else:
            raise UserError(_("Alert!, Hi %s,No products has been selected,Please check it."
                              % self.env.user.name))

        if self.delivery_type:
            self.write({
                'state': 'submitted',
            })
        else:
            raise UserError(_("Alert!, Hi %s,The Request Raised For	is not selected,"
                              "Please select Pharmacy or Operation Theatre to proceed further."
                              % self.env.user.name))

    def _compute_direct_delivery_backorder(self):
        self.direct_delivery_backorder_count = self.env['stock.picking'].sudo().search_count(
            [('origin', '=', self.name), ('backorder_id', '!=', False)])

    def _compute_direct_delivery_picking(self):
        self.direct_delivery_picking_count = self.env['stock.picking'].sudo().search_count(
            [('origin', '=', self.name)])

    def direct_delivery_back_order(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('stock.view_picking_form')
        tree_view = self.sudo().env.ref('stock.vpicktree')
        return {
            'name': _('My Back Order'),
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('origin', '=', self.name), ('backorder_id', '!=', False)],
        }

    def direct_delivery_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_ready')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.stock_picking_id.id)]
        pick_ids = sum([self.stock_picking_id.id])
        if pick_ids:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result

    def set_delivery(self):
        if not self.picking_type_id:
            raise UserError(_(
                " Please select a picking type"))
        for order in self:
            if not self.stock_picking_id:
                pick = {}
                if self.picking_type_id.code == 'outgoing':
                    pick = {
                        # 'delivery_sender': order.delivery_responsible.user_id.employee_id.id,
                        # 'delivery_receiver': order.delivery_request_raised_for.user_id.employee_id.id or
                        #                      order.delivery_responsible.user_id.employee_id.id,
                        'partner_id': order.delivery_responsible.user_id.partner_id.id,
                        # 'purpose': order.purpose,
                        # 'direct_delivery': True,
                        'picking_type_id': order.picking_type_id.id,
                        'origin': order.name,
                        'location_dest_id': order.delivery_responsible.address_id.property_stock_customer.id,
                        'location_id': order.picking_type_id.default_location_src_id.id,
                        'move_type': 'direct'
                    }
                picking = self.env['stock.picking'].create(pick)
                self.stock_picking_id = picking.id
                # self.picking_count = len(picking)
                moves = order.delivery_product_lines.filtered(
                    lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)
                move_ids = moves._action_confirm()
                move_ids._action_assign()
            self.write({'state': 'delivered_create'})
            # else:
            #     raise UserError(_(
            #         "Alert!, The Direct Delivery Indent requested Products has No Stock, \n"
            #         "Please check with PO Team to update the Stock to Delivery."))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('direct.delivery.indent')
        return super(DirectDeliveryIndent, self).create(vals)


class DirectDeliveryIndentLine(models.Model):
    _name = 'direct.delivery.indent.line'
    _description = 'Direct Delivery Indent Line'

    direct_indent_id = fields.Many2one('direct.delivery.indent', 'Indent')

    product_id = fields.Many2one('product.product', 'Product')
    product_required_qty = fields.Float('Quantity Required', digits='Product UoS', default=1)
    qty_shipped = fields.Float('QTY Shipped')
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', related='product_id.uom_id')
    product_available = fields.Float(string='OnHand Qty', related='product_id.qty_available')

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            # price_unit = line.price_unit
            if picking.picking_type_id.code == 'outgoing':
                template = {
                    # 'partner_id': line.responsible.address_id.id,
                    'name': line.product_id.id or '',
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'location_dest_id': line.direct_indent_id.delivery_responsible.address_id.property_stock_customer.id,
                    'picking_id': picking.id,
                    'state': 'assigned',
                    # 'company_id': line.company_id.id,
                    # 'price_unit': price_unit,
                    'picking_type_id': picking.picking_type_id.id,
                    'route_ids': 1 and [
                        (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
            diff_quantity = line.product_required_qty
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
                'quantity_done': diff_quantity,
            })
            template['product_uom_qty'] = diff_quantity
            template['quantity_done'] = diff_quantity
            done += moves.create(template)
        return done
