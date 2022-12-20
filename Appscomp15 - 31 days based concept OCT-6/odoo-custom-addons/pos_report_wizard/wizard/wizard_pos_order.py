from odoo import api, fields, models, _
from datetime import datetime, timedelta, date


class PosProductReportWizard(models.TransientModel):
    _name = 'pos.product.report.wizard'
    _description = "product Report Details"

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    product_boolean = fields.Boolean(string='Is Product Qty')
    product_selection = fields.Selection([('all_products', 'Over All'), ('products', 'Date Wise')],
                                         string='Products', default='products')

    def print_product_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'product_selection': self.product_selection,
            },
        }
        return self.env.ref('pos_report_wizard.report_product_wizard_action').report_action(self, data=data)


class ReportActionRender(models.AbstractModel):
    _name = 'report.pos_report_wizard.report_product_qweb_report'
    _description = 'Product Report Render'

    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        product_selection = data['form']['product_selection']
        date_start = datetime.strptime(start_date, '%Y-%m-%d').date()
        date_end = datetime.strptime(end_date, '%Y-%m-%d').date()

        docs = []
        duplicate_avoid = set()
        date_avoid = []
        record_duplicate = []
        orginal = []

        date_product = []
        pos_product = self.env['pos.order'].search(
            [('date_order', '>=', date_start),
             ('date_order', '<=', date_end)])

        for date in pos_product:
            dates = date.date_order.date()
            if dates not in date_avoid:
                date_avoid.append(dates)

        date_avoid.sort()
        for i in date_avoid:
            products = []
            domain = self.env['pos.order'].search([('order_date', '=', i)])
            if domain:
                for record in domain:
                    for rec in record.lines:
                        # if rec.full_product_name not in products:
                        products.append({
                            'name': rec.full_product_name,
                            'qty': rec.qty,
                            'price_unit': rec.price_unit,
                            'subtotal': rec.price_subtotal,
                        })
                values = {
                    str(i.strftime('%d-%m-%Y')): products,
                }
                date_product.append(values)

        for i in date_product:
            for j in list(i.values())[0]:
                products = j
        # if product_selection == 'all_tems':
        #     print('***********************', )

        if product_selection == 'products':
            for rec in pos_product:
                for record in pos_product.lines:
                    vals = {
                        'product': record.full_product_name,
                        'quantity': record.qty,
                        'price': record.price_unit,
                        'subtotal': record.price_subtotal,
                        'orderdate': date.date_order,
                    }
                    docs.append(vals)


                return {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'docs': docs,
                    'start_date': start_date,
                    'end_date': end_date,
                    'product_selection': product_selection,
                    'date_product': date_product,

                }

        if product_selection == 'all_products':
            for product in pos_product.lines:
                duplicate_list = product.full_product_name
                duplicate_avoid.add(duplicate_list)
                record_duplicate = duplicate_avoid

            for i in duplicate_avoid:
                orginal.append({
                    'name': i,
                    'qty': 0,
                })
            for order in pos_product:
                for line in order.lines:
                    for i in orginal:
                        if line.full_product_name == i['name']:
                            i['qty'] += line.qty
            original_value = orginal

            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': docs,
                'start_date': start_date,
                'end_date': end_date,
                'product_selection': product_selection,
                'duplicate': record_duplicate,
                'orginal': original_value,
            }
