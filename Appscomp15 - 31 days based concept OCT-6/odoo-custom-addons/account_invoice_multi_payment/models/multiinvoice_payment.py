import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class AdvancePayment(models.Model):
    _name = 'advance.payment'

    advance_payment_id = fields.Many2one('account.payment', string='Payment')
    partner_advance_balance_payment_id = fields.Many2one('account.payment', string='Payment Balance')
    payment_name = fields.Char(string='Refund Payment Ref')
    journal_related_id = fields.Many2one('account.move', string='Journal Ref')
    # advance_amount = fields.Monetary(string='Amount')
    total_advance_amount = fields.Monetary(string='Total Amount')
    total_adv_balance_amount = fields.Monetary(string='Total Balance Amount')
    # partner_id = fields.Many2one(string='Total Amount')
    advance_payment_date = fields.Date(string='Payment Date')
    currency_id = fields.Many2one(string='Currency')
    reconcile_amount = fields.Monetary(string='Reconcile Amount')
    refund_reconcile_amount = fields.Monetary(string='Refund Amount')
    advance_allocation = fields.Boolean('Full Reconcile ?', default=False)
    advance_refund_allocation = fields.Boolean('Full Refund ?', default=False)
    refund_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("not_refunded", "Not Refunded"),
            ("no_refund", "NO Refund"),
            ("refunded", "Refund Done"),
        ],
        string="Status",
        compute='_get_refund_state',
        default='draft',
        store=True,
        help="""A standard payment refund process against customer/vendor).""")

    @api.depends('journal_related_id')
    # @api.onchange('journal_related_id')
    def _get_refund_state(self):
        if self.refund_reconcile_amount:
            if self.journal_related_id.state == 'posted':
                self.refund_state = 'refunded'
            elif self.journal_related_id.state != 'posted':
                self.refund_state = 'not_refunded'
        else:
            self.refund_state = 'no_refund'

    @api.onchange('advance_allocation', 'advance_refund_allocation')
    def allocate(self):
        for rec in self:
            if rec.advance_allocation:
                rec.reconcile_amount = rec.total_adv_balance_amount
            else:
                rec.reconcile_amount = 0.0
            if rec.advance_refund_allocation:
                rec.refund_reconcile_amount = rec.total_adv_balance_amount
            else:
                rec.refund_reconcile_amount = 0.0

    #
    def get_line_items(self):
        line_vals = []
        if self.advance_payment_id.payment_type == 'inbound':
            # aa = self.env['ir.config_parameter'].sudo().get_param('account_invoice_multi_payment.transfer_account_id')
            account = self.advance_payment_id.company_id.transfer_account_id
            outstanding = self.advance_payment_id.company_id.account_journal_payment_credit_account_id
            # account = self.env['account.account'].sudo().search([('id', '=', aa)])
            vals = [0, 0, {
                'account_id': account.id,
                # 'partner_id': self.partner_id.id,
                'credit': self.refund_reconcile_amount,
                'debit': False,
                'name': self.advance_payment_id.name + '/' + 'Refund Amount to' +
                        self.advance_payment_id.partner_id.name,
            }]
            line_vals.append(vals)
            vals_2 = [0, 0, {
                # 'partner_id': self.partner_id.id,
                'account_id': outstanding.id,
                'credit': False,
                'debit': self.refund_reconcile_amount,
                'name': self.advance_payment_id.name + '/' + 'Refund Amount to' +
                        self.advance_payment_id.partner_id.name,
            }]
            line_vals.append(vals_2)
        elif self.advance_payment_id.payment_type == 'outbound':
            # aa = self.env['ir.config_parameter'].sudo().get_param('account_invoice_multi_payment.transfer_account_id')
            aa = self.advance_payment_id.company_id.transfer_account_id
            outstanding = self.advance_payment_id.company_id.account_journal_payment_debit_account_id
            # account = self.env['account.account'].sudo().search([('id', '=', aa)])
            account = self.advance_payment_id.company_id.transfer_account_id
            vals = [0, 0, {
                'account_id': account.id,
                # 'partner_id': self.partner_id.id,
                'credit': False,
                'debit': self.amount,
                'name': self.advance_payment_id.name + '/' + 'Refund Amount to' +
                        self.advance_payment_id.partner_id.name,
            }]
            line_vals.append(vals)
            vals_2 = [0, 0, {
                # 'partner_id': self.partner_id.id,
                'account_id': outstanding.id,
                'credit': self.amount,
                'debit': False,
                'name': self.advance_payment_id.name + '/' + 'Refund Amount to' +
                        self.advance_payment_id.partner_id.name,
            }]
            line_vals.append(vals_2)
        return line_vals

    def full_refund(self):
        rec = self.env["account.move"].sudo().create({
            "ref": 'Refund Amount to' + self.advance_payment_id.partner_id.name,
            "line_ids": self.get_line_items(),
        })
        self.write({
            'journal_related_id': rec.id,
        })


class AccountPaymentInvoices(models.Model):
    _name = 'account.payment.invoice'

    invoice_id = fields.Many2one('account.move', string='Invoice')
    payment_id = fields.Many2one('account.payment', string='Payment')
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    origin = fields.Char(related='invoice_id.invoice_origin')
    date_invoice = fields.Date(related='invoice_id.invoice_date')
    date_due = fields.Date(related='invoice_id.invoice_date_due')
    payment_state = fields.Selection(related='payment_id.state', store=True)
    invoice_payment_state = fields.Selection(related='invoice_id.payment_state', store=True)
    reconcile_amount = fields.Monetary(string='Allocation')
    amount_total = fields.Monetary(related="invoice_id.amount_total", string='Original Amount')
    residual = fields.Monetary(related="invoice_id.amount_residual", string='Outstanding Amount')
    allocation = fields.Boolean('Full Reconcile ?', default=False)

    @api.onchange('allocation')
    def allocate(self):
        for rec in self:
            if rec.allocation:
                rec.reconcile_amount = rec.residual
            else:
                rec.reconcile_amount = 0.0


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_id = fields.Many2one('account.move', string='Invoice')

    def reconcile(self):
        ''' Reconcile the current move lines all together.
        :return: A dictionary representing a summary of what has been done during the reconciliation:
                * partials:             A recorset of all account.partial.reconcile created during the reconciliation.
                * full_reconcile:       An account.full.reconcile record created when there is nothing left to reconcile
                                        in the involved lines.
                * tax_cash_basis_moves: An account.move recordset representing the tax cash basis journal entries.
        '''
        results = {}

        if not self:
            return results

        # List unpaid invoices
        not_paid_invoices = self.move_id.filtered(
            lambda move: move.is_invoice(include_receipts=True) and move.payment_state not in ('paid', 'in_payment')
        )

        # ==== Check the lines can be reconciled together ====
        company = None
        account = None
        # print("===self==", self)
        for line in self:
            if line.reconciled:
                raise UserError(_("You are trying to reconcile some entries that are already reconciled."))
            if not line.account_id.reconcile and line.account_id.internal_type != 'liquidity':
                raise UserError(
                    _("Account %s does not allow reconciliation. First change the configuration of this account to "
                      "allow it.")
                    % line.account_id.display_name)
            if line.move_id.state != 'posted':
                raise UserError(_('You can only reconcile posted entries.'))
            if company is None:
                company = line.company_id
            elif line.company_id != company:
                raise UserError(_("Entries doesn't belong to the same company: %s != %s")
                                % (company.display_name, line.company_id.display_name))
            if account is None:
                account = line.account_id
            elif line.account_id != account:
                raise UserError(_("Entries are not from the same account: %s != %s")
                                % (account.display_name, line.account_id.display_name))

        sorted_lines = self.sorted(key=lambda line: (line.date_maturity or line.date, line.currency_id))

        # ==== Collect all involved lines through the existing reconciliation ====

        involved_lines = sorted_lines
        involved_partials = self.env['account.partial.reconcile']
        current_lines = involved_lines
        current_partials = involved_partials
        while current_lines:
            current_partials = (current_lines.matched_debit_ids + current_lines.matched_credit_ids) - current_partials
            involved_partials += current_partials
            current_lines = (current_partials.debit_move_id + current_partials.credit_move_id) - current_lines
            involved_lines += current_lines

        # ==== Create partials ====

        partial_amount = self.env.context.get('amount', False)
        if partial_amount:
            reconcile = sorted_lines._prepare_reconciliation_partials()
            reconcile[0].update({
                'amount': partial_amount,
                'debit_amount_currency': partial_amount,
                'credit_amount_currency': partial_amount,
            })
        else:
            reconcile = sorted_lines._prepare_reconciliation_partials()

        partials = self.env['account.partial.reconcile'].create(reconcile)
        # Track newly created partials.
        results['partials'] = partials
        involved_partials += partials

        # ==== Create entries for cash basis taxes ====

        is_cash_basis_needed = account.user_type_id.type in ('receivable', 'payable')
        if is_cash_basis_needed and not self._context.get('move_reverse_cancel'):
            tax_cash_basis_moves = partials._create_tax_cash_basis_moves()
            results['tax_cash_basis_moves'] = tax_cash_basis_moves

        # ==== Check if a full reconcile is needed ====

        if involved_lines[0].currency_id and all(
                line.currency_id == involved_lines[0].currency_id for line in involved_lines):
            is_full_needed = all(line.currency_id.is_zero(line.amount_residual_currency) for line in involved_lines)
        else:
            is_full_needed = all(line.company_currency_id.is_zero(line.amount_residual) for line in involved_lines)
        if is_full_needed:

            # ==== Create the exchange difference move ====

            if self._context.get('no_exchange_difference'):
                exchange_move = None
            else:
                exchange_move = involved_lines._create_exchange_difference_move()
                if exchange_move:
                    exchange_move_lines = exchange_move.line_ids.filtered(lambda line: line.account_id == account)

                    # Track newly created lines.
                    involved_lines += exchange_move_lines

                    # Track newly created partials.
                    exchange_diff_partials = exchange_move_lines.matched_debit_ids \
                                             + exchange_move_lines.matched_credit_ids
                    involved_partials += exchange_diff_partials
                    results['partials'] += exchange_diff_partials

                    exchange_move._post(soft=False)

            # ==== Create the full reconcile ====

            results['full_reconcile'] = self.env['account.full.reconcile'].create({
                'exchange_move_id': exchange_move and exchange_move.id,
                'partial_reconcile_ids': [(6, 0, involved_partials.ids)],
                'reconciled_line_ids': [(6, 0, involved_lines.ids)],
            })

        # Trigger action for paid invoices
        not_paid_invoices \
            .filtered(lambda move: move.payment_state in ('paid', 'in_payment')) \
            .action_invoice_paid()

        return results


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_payment_diff_account(self):
        inbound_code = 213200
        outbound_code = 201200
        payment_diff_code = self.sudo().env['account.account'].search([('code', '=', inbound_code)])
        return payment_diff_code

    payment_invoice_ids = fields.One2many('account.payment.invoice', 'payment_id', string="Customer Invoices")
    advance_payment_ids = fields.One2many('advance.payment', 'advance_payment_id', string="Advance Payment")
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False,
                             compute='get_total_advance_amount')
    payment_difference = fields.Monetary(
        compute='_compute_payment_difference')
    effective_date = fields.Date(string='Effective Date')
    # payment_difference_handling = fields.Selection([
    #     ('open', 'Keep open'),
    #     ('reconcile', 'Mark as fully paid'),
    # ], default='open', string="Payment Difference Handling")
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", copy=False,
                                          domain="[('deprecated', '=', False),"
                                                 " ('company_id', '=', company_id)]",
                                          default=_get_payment_diff_account)
    writeoff_label = fields.Char(string='Journal Item Label', default='Write-Off',
                                 help='Change label of the counterpart that will hold the payment difference')
    # line_length = fields.Char(string='Length')
    line_length_check = fields.Boolean(string='Length')
    advance_balance_amount = fields.Monetary(string='Balance Amount')
    total_advance_balance_amount = fields.Monetary(string='Total Advance Balance Amount')
    advance_amount_balance_count = fields.Integer(string='Balance Amount', compute='get_advance_count')

    # payment_difference = fields.Float(string='Difference Amount', readonly=True)
    handling = fields.Selection([('open', 'Keep open'),
                                 ('reconcile', 'Mark invoice as fully paid')],
                                default='open',
                                string="Action",
                                copy=False)
    comment = fields.Char('Counterpart Comment', readonly=True, default='Write-Off',
                          states={'draft': [('readonly', False)]})
    writeoff_amount = fields.Float(string='Difference Amount', readonly=True, compute='get_write_off_amounts',
                                   store=True,
                                   help="Computed as the difference between the amount stated in the voucher and the "
                                        "sum of allocation on the voucher lines.")
    payment_option = fields.Selection([
        ('without_writeoff', 'Keep Open'),
        ('with_writeoff', 'Reconcile Payment Balance'),
    ], 'Payment Difference', default='without_writeoff', readonly=True, states={'draft': [('readonly', False)]},
        help="This field helps you to choose what you want to do with the eventual difference between the paid amount "
             "and the sum of allocated amounts. You can either choose to keep open this difference on the partner's "
             "account, or reconcile it with the payment(s)")
    writeoff_acc_id = fields.Many2one('account.account', 'Counterpart Account', readonly=True,
                                      states={'draft': [('readonly', False)]})

    display_all_advance = fields.Boolean(string='Show All Advance')

    # writeoff_account_id = fields.Many2one('account.account', string="Account",
    #                                       copy=False)

    @api.depends('advance_payment_ids.reconcile_amount')
    @api.onchange('advance_payment_ids.reconcile_amount')
    def get_total_advance_amount(self):
        for rec in self:
            amount = 0.0
            advance_bal_amount = 0.0
            for bool in rec.advance_payment_ids:
                if bool.advance_allocation:
                    amount += bool.reconcile_amount
                else:
                    amount += bool.reconcile_amount
            rec.amount += amount

    def advance_balance_deductions(self):
        diff = 0.00
        if self.advance_payment_ids:
            for advanced in self.advance_payment_ids:
                diff = advanced.partner_advance_balance_payment_id.advance_balance_amount - advanced.reconcile_amount
                if advanced.journal_related_id:
                    diff = advanced.partner_advance_balance_payment_id.advance_balance_amount - \
                           (advanced.reconcile_amount + advanced.refund_reconcile_amount)
            self.advance_payment_ids.write({
                'total_adv_balance_amount': diff,
            })
            advanced.partner_advance_balance_payment_id.write({
                'advance_balance_amount': self.advance_payment_ids.total_adv_balance_amount
            })

    @api.onchange('display_all_advance')
    def _display_all_advance_details(self):
        print('===============')

    @api.depends('payment_invoice_ids')
    def get_write_off_amounts(self):
        for rec in self:
            amount = 0.0
            receive_amount = 0.0
            writeoff_amount = 0.0
            amount = rec.amount
            for all in rec.payment_invoice_ids:
                writeoff_amount += all.reconcile_amount
                amount = rec.amount
            # for pay in rec.payment_item_ids:
            #     receive_amount += pay.amount
            rec.writeoff_amount = amount - writeoff_amount
            # rec.writeoff_amount = (amount + receive_amount) - writeoff_amount

    def get_advance_count(self):
        self.advance_amount_balance_count = self.env['account.payment'].search_count([
            ('advance_balance_amount', '!=', 0), ('state', '=', 'posted'),
            ('partner_id', '=', self.partner_id.id)])

    def get_advance_amount_balance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Partner Balance Advance Payment',
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'domain': [('advance_balance_amount', '!=', 0),
                       ('partner_id', '=', self.partner_id.id), ('state', '=', 'posted')],
        }

    @api.depends('payment_invoice_ids')
    def get_amounts(self):
        for rec in self:
            amount = 0.0
            for all in rec.payment_invoice_ids:
                amount += all.reconcile_amount
            # if amount > self.amount:
            #     raise UserError(
            #         _("Alert!, The Reconcile Amount %s Total must be Smaller than Amount %s") % (amount, self.amount))

    def get_advance_balance_amount(self):
        payment_id = self.env['account.payment'].search([('advance_balance_amount', '!=', 0),
                                                         ('state', '=', 'posted'),
                                                         ('partner_id', '=', self.partner_id.id)])
        ad_amount = 0
        for ids in payment_id:
            ad_amount += ids.advance_balance_amount
            self.total_advance_balance_amount = ad_amount

    def refund_partner_advance_balance_payment(self):
        if self.advance_balance_amount:
            raise ValidationError('Yes, The Refund button is calling')

    def add_to_advance_amount(self):
        payment_id = self.env['account.payment'].search([('advance_balance_amount', '!=', 0),
                                                         ('state', '=', 'posted'),
                                                         ('partner_id', '=', self.partner_id.id)])
        for ids in payment_id:
            ids.advance_balance_amount = 0.00
        self.amount += self.total_advance_balance_amount
        self.total_advance_balance_amount = 0

    @api.onchange('partner_id')
    def _onchange_partner_balance_advance(self):
        # payment_id = self.env['account.payment'].search([('advance_balance_amount', '!=', 0),
        #                                                  ('state', '=', 'posted'),
        #                                                  ('partner_id', '=', self.partner_id.id)])
        # for advance_id in payment_id:
        if self.payment_type in ['inbound', 'outbound'] and self.partner_type and self.partner_id \
                and self.currency_id:
            self.advance_payment_ids = [(6, 0, [])]
            payment_invoice_values = []
            if self.payment_type == 'inbound' and self.partner_type == 'customer':
                invoice_recs = self.env['account.payment'].sudo().search([
                    ('amount', '!=', 0),
                    ('advance_balance_amount', '!=', 0),
                    ('state', '=', 'posted'),
                    ('partner_id', '=', self.partner_id.id)
                ])
                if invoice_recs:
                    for inv_id in invoice_recs:
                        payment_invoice_values.append([0, 0, {
                            'advance_payment_id': inv_id.id,
                            'partner_advance_balance_payment_id': inv_id.id,
                            'payment_name': inv_id.name,
                            'advance_payment_date': inv_id.date,
                            'total_advance_amount': inv_id.amount,
                            'total_adv_balance_amount': inv_id.advance_balance_amount,
                            # 'payment_state': inv_id.state,
                        }])
                        # payment_invoice_values.append(([0, 0,]))
                    # payment_invoice_values.append([0, 0 , invoice_recs])
                    # for invoice_rec in invoice_recs:
                    #     payment_invoice_values.append([0, 0, {'name': invoice_rec.id}])
                    # print('=====================================', payment_invoice_values)
                    self.advance_payment_ids = payment_invoice_values

    def get_advance_balance_amount(self):
        advance_amount = self.amount
        total_amount = 0
        invoice_id = invoice_recs = self.env['account.move'].search([('id', 'in', self.reconciled_invoice_ids.ids)])
        for val in invoice_id:
            dict_val = val.invoice_payments_widget
            res = json.loads(dict_val)
            # print('***************************************************', self.name, type(res))
            for list_item in res['content']:
                if self.name == list_item['ref']:
                    # print('LIST+++++++++++++++++++++++++++++++++++', list_item['amount'])
                    total_amount += float(list_item['amount'])
            self.advance_balance_amount = self.amount - total_amount

    # @api.onchange('amount')
    # def _onchange_reconcile_amount(self):
    #     payment_invoice_values = []
    #     extra_amount = 0
    #     if self.amount and self.payment_invoice_ids:
    #         bal_amount = self.amount / len(self.payment_invoice_ids)
    #         min_invoice_ids = [min_id.invoice_id for min_id in self.payment_invoice_ids\
    #                            if min_id.invoice_id.amount_residual < bal_amount]
    #         max_invoice_ids = [max_id.invoice_id for max_id in self.payment_invoice_ids\
    #                            if max_id.invoice_id.amount_residual > bal_amount]
    #         for min_inv in min_invoice_ids:
    #             payment_invoice_values.append([0, 0, {
    #                 'invoice_id': min_inv.id,
    #                 'reconcile_amount': min_inv.amount_residual
    #             }])
    #             if max_invoice_ids:
    #                 extra_amount += (bal_amount - min_inv.amount_residual) / len(max_invoice_ids)
    #         bal_amount += extra_amount
    #         for max_inv in max_invoice_ids:
    #             payment_invoice_values.append([0, 0, {
    #                 'invoice_id': max_inv.id,
    #                 'reconcile_amount': bal_amount
    #             }])
    #         self.payment_invoice_ids = [(6, 0, [])]
    #         self.payment_invoice_ids = payment_invoice_values

    @api.depends('amount')
    def _compute_payment_difference(self):
        for payment in self:
            if payment.payment_invoice_ids:
                if payment.amount < sum(payment.payment_invoice_ids.mapped('reconcile_amount')):
                    payment.payment_difference = sum(
                        payment.payment_invoice_ids.mapped('reconcile_amount')) - payment.amount
                else:
                    payment.payment_difference = 0.0
            else:
                payment.payment_difference = 0.0

    @api.onchange('payment_type', 'partner_type', 'partner_id', 'currency_id')
    def _onchange_to_get_vendor_invoices(self):
        if self.payment_type in ['inbound', 'outbound'] and self.partner_type and self.partner_id and self.currency_id:
            self.payment_invoice_ids = [(6, 0, [])]
            if self.payment_type == 'inbound' and self.partner_type == 'customer':
                invoice_type = 'out_invoice'
            elif self.payment_type == 'outbound' and self.partner_type == 'customer':
                invoice_type = 'out_refund'
            elif self.payment_type == 'outbound' and self.partner_type == 'supplier':
                invoice_type = 'in_invoice'
            else:
                invoice_type = 'in_refund'
            invoice_recs = self.env['account.move'].search([
                ('partner_id', 'child_of', self.partner_id.id),
                ('state', '=', 'posted'),
                ('move_type', '=', invoice_type),
                ('payment_state', '!=', 'paid'),
                ('currency_id', '=', self.currency_id.id)])
            payment_invoice_values = []
            for invoice_rec in invoice_recs:
                payment_invoice_values.append([0, 0, {'invoice_id': invoice_rec.id}])
            self.payment_invoice_ids = payment_invoice_values
            if len(self.payment_invoice_ids) == 0:
                self.line_length_check = True
            else:
                self.line_length_check = False

    def action_post(self):
        self.advance_balance_deductions()
        super(AccountPayment, self).action_post()

        for payment in self:
            # if payment.payment_invoice_ids: if payment.amount < sum(payment.payment_invoice_ids.mapped(
            # 'reconcile_amount')): raise UserError(_("The sum of the reconcile amount of listed invoices are greater
            # than payment's amount."))

            for line_id in payment.payment_invoice_ids:
                if not line_id.reconcile_amount:
                    continue
                if line_id.amount_total <= line_id.reconcile_amount:
                    self.ensure_one()
                    if payment.payment_type == 'inbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0)
                        lines += line_id.invoice_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()
                    elif payment.payment_type == 'outbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0)
                        lines += line_id.invoice_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()
                else:
                    self.ensure_one()
                    if payment.payment_type == 'inbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0)
                        lines += line_id.invoice_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.with_context(amount=line_id.reconcile_amount).reconcile()
                    elif payment.payment_type == 'outbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0)
                        lines += line_id.invoice_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.with_context(amount=line_id.reconcile_amount).reconcile()
        return True

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}
        # if self.payment_method_id.code == 'pdc':
        #
        # if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id: raise
        # UserError(_( "You can't create a new payment without an outstanding payments/receipts account set on the %s
        # journal.", self.journal_id.display_name))
        #
        #     # Compute amounts.
        #     write_off_amount = write_off_line_vals.get('amount', 0.0)
        #     if self.payment_difference != 0 and write_off_amount == 0:
        #         write_off_amount = self.payment_difference
        #
        #     if self.payment_type == 'inbound':
        #         # Receive money.
        #         counterpart_amount = -self.amount
        #         write_off_amount *= -1
        #     elif self.payment_type == 'outbound':
        #         # Send money.
        #         counterpart_amount = self.amount
        #     else:
        #         counterpart_amount = 0.0
        #         write_off_amount = 0.0
        #
        #     balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id,
        #                                         self.date)
        #     counterpart_amount_currency = counterpart_amount
        #     write_off_balance = self.currency_id._convert(write_off_amount, self.company_id.currency_id,
        #                                                   self.company_id, self.date)
        #     write_off_amount_currency = write_off_amount
        #     currency_id = self.currency_id.id
        #
        #     if self.is_internal_transfer:
        #         if self.payment_type == 'inbound':
        #             liquidity_line_name = _('Transfer to %s', self.journal_id.name)
        #         else:  # payment.payment_type == 'outbound':
        #             liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        #     else:
        #         liquidity_line_name = self.payment_reference
        #
        #     # Compute a default label to set on the journal items.
        #
        #     payment_display_name = {
        #         'outbound-customer': _("Customer Reimbursement"),
        #         'inbound-customer': _("Customer Payment"),
        #         'outbound-supplier': _("Vendor Payment"),
        #         'inbound-supplier': _("Vendor Reimbursement"),
        #     }
        #
        #     default_line_name = self.env['account.move.line']._get_default_line_name(
        #         _("Internal Transfer") if self.is_internal_transfer else payment_display_name[
        #             '%s-%s' % (self.payment_type, self.partner_type)],
        #         self.amount,
        #         self.currency_id,
        #         self.date,
        #         partner=self.partner_id,
        #     )
        #
        # line_vals_list = [ # Liquidity line. { 'name': liquidity_line_name or default_line_name, 'date_maturity':
        # self.date, 'amount_currency': -counterpart_amount_currency, 'currency_id': currency_id, 'debit': balance <
        # 0.0 and -balance or 0.0, 'credit': balance > 0.0 and balance or 0.0, 'partner_id': self.partner_id.id,
        # 'account_id': self.pdc_account.id, }, # Receivable / Payable. { 'name': self.payment_reference or
        # default_line_name, 'date_maturity': self.date, 'amount_currency': counterpart_amount_currency +
        # write_off_amount_currency if currency_id else 0.0, 'currency_id': currency_id, 'debit': balance +
        # write_off_balance > 0.0 and balance + write_off_balance or 0.0, 'credit': balance + write_off_balance < 0.0
        # and -balance - write_off_balance or 0.0, 'partner_id': self.partner_id.id, 'account_id':
        # self.destination_account_id.id, }, ] if write_off_balance: # Write-off line. if self.payment_difference !=
        # 0: line_vals_list.append({ 'name': self.writeoff_label, 'amount_currency': -write_off_amount_currency,
        # 'currency_id': currency_id, 'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
        # 'credit': write_off_balance > 0.0 and write_off_balance or 0.0, 'partner_id': self.partner_id.id,
        # 'account_id': self.writeoff_account_id.id, }) else: line_vals_list.append({ 'name':
        # write_off_line_vals.get('name') or default_line_name, 'amount_currency': -write_off_amount_currency,
        # 'currency_id': currency_id, 'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
        # 'credit': write_off_balance > 0.0 and write_off_balance or 0.0, 'partner_id': self.partner_id.id,
        # 'account_id': write_off_line_vals.get('account_id'), }) else:
        if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                self.journal_id.display_name))

        # Compute amounts.
        write_off_amount = write_off_line_vals.get('amount', 0.0)
        # raise UserError(write_off_amount)
        if self.payment_difference != 0 and write_off_amount == 0:
            write_off_amount = self.payment_difference

        if self.payment_type == 'inbound':
            # Receive money.
            counterpart_amount = -self.amount
            write_off_amount *= -1
        elif self.payment_type == 'outbound':
            # Send money.
            counterpart_amount = self.amount
        else:
            counterpart_amount = 0.0
            write_off_amount = 0.0

        balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id,
                                            self.date)
        counterpart_amount_currency = counterpart_amount
        write_off_balance = self.currency_id._convert(write_off_amount, self.company_id.currency_id,
                                                      self.company_id, self.date)
        write_off_amount_currency = write_off_amount
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else:  # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name[
                '%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': -counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': balance < 0.0 and -balance or 0.0,
                'credit': balance > 0.0 and balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency + write_off_amount_currency if currency_id else 0.0,
                'currency_id': currency_id,
                'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]

        if write_off_balance:
            # Write-off line.
            if self.payment_difference != 0:
                line_vals_list.append({
                    'name': self.writeoff_label,
                    'amount_currency': -write_off_amount_currency,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.writeoff_account_id.id,
                })
            else:
                line_vals_list.append({
                    'name': write_off_line_vals.get('name') or default_line_name,
                    'amount_currency': -write_off_amount_currency,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': write_off_line_vals.get('account_id'),
                })
        return line_vals_list

    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            if line.account_id in (
                    self.journal_id.default_account_id,
                    self.journal_id.payment_debit_account_id,
                    self.journal_id.payment_credit_account_id,
                    # self.journal_id.pdc_account,
            ):
                liquidity_lines += line
            elif line.account_id.internal_type in (
                    'receivable', 'payable') or line.partner_id == line.company_id.partner_id:
                counterpart_lines += line
            else:
                writeoff_lines += line

        return liquidity_lines, counterpart_lines, writeoff_lines


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_debit_account_id = fields.Many2one('account.account', string='Default Debit Account')
    payment_credit_account_id = fields.Many2one('account.account', string='Default Credit Account')
    # payment_credit_account_id = fields.Many2one('account.account', string='Default Credit Account')
