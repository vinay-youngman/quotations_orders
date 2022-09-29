# -*- coding: utf-8 -*-
import json

from odoo import models, fields, api, _

import logging
import requests
from odoo import api, models
import traceback
from datetime import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


# class ResPartnerInherited(models.Model):
#     _inherit = 'res.partner'
#
#     def name_get(self):
#         result = []
#         for rec in self:
#             if rec.is_customer_branch:
#                 result.append((rec.id, '%s - %s' % (rec.gstn, rec.state_id.name)))
#             else:
#                 result.append((rec.id, rec.name))
#         return result


class SaleOrderInherit(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'IN')], limit=1)
        return country

    jobsite_id = fields.Many2one('jobsite', string='Site Name')
    tentative_quo = fields.Boolean('Tentative Quotation', default=False)
    partner_id = fields.Many2one(comodel_name='res.partner', domain="[('is_customer_branch', '=', False)]")
    validity_date = fields.Date(invisible=True)
    job_order = fields.Char(string="Job Order")

    place_of_supply = fields.Many2one("res.country.state", string='Place of Supply', ondelete='restrict', domain="[('country_id', '=', billing_country_id)]")
    rental_advance = fields.Char(string="Rental Advance")
    rental_order = fields.Char(string="Rental Order")
    security_cheque = fields.Char(string="Security Cheque")
    # amendment_doc = fields.Char(string="Amendment Doc")
    # released_at = fields.Datetime(string="Released At")
    # reason_of_release = fields.Selection([
    #     ('customer_request', 'Customer Request'),
    #     ('order_fullfilled', 'Order Fulfilled'),
    #     ('reason_of_release', 'Reason of Release')],
    #     string="Reason of Release")
    # is_authorized = fields.Boolean(string="Is Authorized", default=False)
    # part_pickup = fields.Boolean(string="Part Pickup", default=False)
    remark = fields.Char(string="Remark")

    customer_branch = fields.Many2one(comodel_name='res.partner', string='Customer GSTs', domain="[('is_company', "
                                                                                                   "'=', True), "
                                                                                                   "('is_customer_branch', '=', True), ('parent_id', '=', partner_id)]")
    # @api.model
    # def _amount_all(self):
    #     super(SaleOrderInherit, self)._amount_all()
    #     for order in self:
    #         account_move = self.env['account.move']
    #
    #         tax_lines_data = [{
    #             'line_key': 'base_line_0',
    #             'base_amount': tax_results['total_excluded'],
    #             'tax': current_tax,
    #         }]
    #
    #         amount_untaxed = order.amount_untaxed + order.freight_amount
    #         amount_tax = order.amount_tax + 5
    #
    #         order.update({
    #             'amount_untaxed': amount_untaxed,
    #             'amount_tax': amount_tax,
    #             'amount_total': amount_untaxed + amount_tax,
    #         })

    # @api.model
    # def _compute_tax_totals_json(self):

    #     account_move = self.env['account.move']
    #     for order in self:
    #         order.amount_untaxed = order.freight_amount
    #         tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
    #         tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
    #         order.tax_totals_json = json.dumps(tax_totals)


    po_number = fields.Char(string="PO Number")
    po_amount = fields.Char(string="PO Amount")
    po_date = fields.Date(string='PO Date')

    beta_quot_id = fields.Integer()

    # Billing Address
    billing_street = fields.Char(string="Billing Address")
    billing_street2 = fields.Char()
    billing_city = fields.Char()
    billing_country_id = fields.Many2one('res.country', string='Billing Country', ondelete='restrict',
                                         default=_get_default_country)
    billing_state_id = fields.Many2one("res.country.state", string='Billing State', ondelete='restrict',
                                       domain="[('country_id', '=', billing_country_id)]")

    billing_zip = fields.Char(string='Billing Pincode', change_default=True)

    # Delivery Address
    delivery_street = fields.Char(string="Delivery Address")
    delivery_street2 = fields.Char()
    delivery_city = fields.Char()
    delivery_country_id = fields.Many2one('res.country', string='Delivery Country', ondelete='restrict',
                                          default=_get_default_country)
    delivery_state_id = fields.Many2one("res.country.state", string='Delivery State', ondelete='restrict',
                                        domain="[('country_id', '=', delivery_country_id)]")

    delivery_zip = fields.Char(string='Delivery Pincode', change_default=True)
    email_to = fields.Char(string='Email To')
    email_cc = fields.Char(string='Email CC')

    pickup_date = fields.Date('Pickup Date')

    @api.model
    def _get_default_godowns(self):
        godown = self.env['jobsite.godown'].search([('id', 'in', self.jobsite_id.godown_id)]).name
        return godown

    #jobsite_godowns = fields.Boolean(related='jobsite_id.godown_ids', store=False)
    godown = fields.Many2one("jobsite.godown", string='Godown', ondelete='restrict')
    bill_godown = fields.Many2one("jobsite.godown", string='Billing Godown', ondelete='restrict')

    delivery_date = fields.Date('Delivery Date')

    security_amount = fields.Monetary(string="Security Amount", currency_field='currency_id')
    freight_amount = fields.Monetary(string="Freight Amount", currency_field='currency_id')
    freight_paid_by = fields.Selection([
        ('freight_type1', 'It has been agreed 1st Dispatch and final Pickup will be done by Youngman'),
        ('freight_type2',
         'It has been agreed 1st Dispatch will be done by Youngman and final Pickup will be done by Customer on his '
         'cost'),
        ('freight_type3',
         'It has been agreed 1st Dispatch will be done by Customer on his cost and final Pickup would be done by '
         'Youngman'),
        ('freight_type4',
         'It has been agreed 1st Dispatch will be done by Customer on his cost and final Pickup is already paid by '
         'Customer'),
        ('freight_type5', 'It has been agreed 1st Dispatch and final Pickup will be done by Customer on his cost')],
        string="Freight To Be Paid By : ",
        default='freight_type1')

    price_type = fields.Selection([
        ('daily', 'Daily'),
        ('monthly', 'Monthly')],
        string="Price Type",
        default='monthly')
    purchaser_name = fields.Many2one("res.partner", string='Purchaser Name',
                                     domain="[('parent_id', '=', customer_branch),('category_id','ilike','purchaser'),('is_company','=', False)]")
    purchaser_phone = fields.Char(string='Purchaser Contact Phone')
    purchaser_email = fields.Char(string='Purchaser Email')
    below_min_price = fields.Boolean('Below Min Price', default=False)

    otp = fields.Integer(string='OTP', store=False)
    otp_verified = fields.Boolean(string='OTP', store=False, default=False)  # TODO compute field should be equal to

    is_rental_advance = fields.Boolean(related='customer_branch.rental_advance', store=False)
    is_rental_order = fields.Boolean(related='customer_branch.rental_order', store=False)
    is_security_cheque = fields.Boolean(related='customer_branch.security_cheque', store=False)

    rental_advance = fields.Binary(string="Rental Advance")
    rental_order = fields.Binary(string="Rental Order")
    security_cheque = fields.Binary(string="Security Cheque")

    # def check_customer_validation(self, vals):
    #     if not vals['tentative_quo']:
    #         if (self.partner_id.is_company == False) or (self.partner_id.is_customer_branch == True):
    #             raise ValidationError(_("Please select a Company"))

    @api.model
    def _amount_all(self):
        super(SaleOrderInherit, self)._amount_all()
        for order in self:
            #TODO: get tax rate from config
            tax_rate = 0.28

            amount_untaxed = order.amount_untaxed + order.freight_amount
            amount_tax = order.amount_tax + (order.freight_amount * tax_rate)

            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'freight_amount')
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = order_line.order_id
            return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                         product=order_line.product_id,
                                                         partner=order.partner_shipping_id)

        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)

            tax_lines_data.append({'line_key': "tax_line_NewId_'virtual_0'_24", "tax_amount": order.freight_amount * 0.28, "tax": self.env['account.tax'].sudo().search([('id', '=', '24')])})
            tax_lines_data.append({'line_key': "base_line_NewId_'virtual_0'", "base_amount": order.freight_amount, "tax": self.env['account.tax'].sudo().search([('id', '=', '24')])})

            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                      order.amount_untaxed, order.currency_id)
            order.tax_totals_json = json.dumps(tax_totals)


    # @api.model
    # def create(self, vals):
    #     self.check_customer_validation(vals)
    #     return super(SaleOrderInherit, self).create(vals)
    #
    # @api.model
    # def write(self, vals):
    #     self.check_customer_validation(vals)
    #     return super(SaleOrderInherit, self).write(vals)

    def action_confirm(self):
        if self.tentative_quo:
            raise ValidationError(_("Confirmation of tentative quotation is not allowed"))
        if not self.po_number:
            raise ValidationError(_('PO Number is mandatory for confirming a quotation'))
        if self.rental_order is None and self.customer_branch.rental_order is True:
            raise ValidationError(_('Rental Order is mandatory for this customer'))
        if self.rental_advance is None and self.customer_branch.rental_advance is True:
            raise ValidationError(_('Rental Advance is mandatory for this customer'))
        if self.security_cheque is None and self.customer_branch.security_cheque is True:
            raise ValidationError(_('Security Cheque is mandatory for this customer'))

        res = super(SaleOrderInherit, self).action_confirm()

    @api.onchange('godown')
    def get_bill_godown(self):
        if self.godown:
            self.bill_godown = self.godown

    @api.onchange('purchaser_name')
    def get_purchaser_phone(self):
        if self.purchaser_name:
            self.purchaser_phone = self.purchaser_name.phone
            self.purchaser_email = self.purchaser_name.email

    @api.onchange('jobsite_id')
    def get_delivery_address(self):
        if self.jobsite_id:
            self.delivery_street = self.jobsite_id.street
            self.delivery_street2 = self.jobsite_id.street2
            self.delivery_city = self.jobsite_id.city
            self.delivery_state_id = self.jobsite_id.state_id
            self.delivery_country_id = self.jobsite_id.country_id
            self.delivery_zip = self.jobsite_id.zip
            self.godown = self.jobsite_id.godown_id

    @api.onchange('partner_id')
    def clear_customer_branch(self):
        if self.partner_id:
            self.customer_branch = False
            self.billing_street = False
            self.billing_street2 = False
            self.billing_city = False
            self.billing_state_id = False
            self.billing_zip = False
            self.billing_country_id = False

        if ((self.partner_id) and (self.tentative_quo is False)) and ((self.partner_id.is_company is False) or (self.partner_id.is_customer_branch is True)):
            raise ValidationError(_("Please select a Company"))

    @api.onchange('customer_branch')
    def get_billing_address(self):
        if self.customer_branch:
            self.billing_street = self.customer_branch.street
            self.billing_street2 = self.customer_branch.street2
            self.billing_city = self.customer_branch.city
            self.billing_state_id = self.customer_branch.state_id
            self.billing_zip = self.customer_branch.zip

    def verify_otp(self):
        otp = self._generate_otp()
        if self.otp == otp:
            self.below_min_price = True
            # self.otp_verified = True
            return {
                'warning': {'title': 'OTP Verified',
                            'message': 'OTP has been verified.', },
            }
        else:
            return {
                'warning': {'title': 'Warning',
                            'message': 'OTP did not match. Please try again.', },
            }

    def request_otp(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('ym_sms.api_key')
        endpoint = self.env['ir.config_parameter'].sudo().get_param('ym_sms.url')
        sender = self.env['ir.config_parameter'].sudo().get_param('ym_sms.sender')
        number = self.env['ir.config_parameter'].sudo().get_param('ym_sms.sales_head_contact')

        otp = self._generate_otp()

        url = "%s?apikey=%s&text=OTP:- %s Youngman India Pvt. Ltd.&mobileno=%s&sender=%s" % (
            endpoint, api_key, str(otp), number, sender)

        try:
            response = requests.request("POST", url, headers={}, data={})
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            tb = traceback.format_exc()
            _logger.error(tb.print_exc())
            return {
                'warning': {'title': 'Warning',
                            'message': 'Could not send OTP', },
            }

        return {
            'info': {'title': 'Warning',
                     'message': 'Could not send OTP', },
        }

    def _generate_otp(self):
        now = datetime.now()

        code = now.year * now.month * now.day * now.hour * now.minute
        code = str(code * 1000000)

        return code[:6]



class ProductTemplateInherit(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    detailed_type = fields.Selection(default='service', readonly=True)
    invoice_policy = fields.Selection(default='delivery', readonly=True)


    status = fields.Selection([
        ('0', 'ACTIVE'),
        ('1', 'DEACTIVE'),
        ('2', 'DISABLE'),
    ], string='Status')

    bundle = fields.Boolean(default=False, string="Bundle")
    consumable = fields.Boolean(default=False, string="Consumable")
    serialized = fields.Boolean(default=False, string="Serialized")
    list_price = fields.Float('Rental Price', digits=(12, 2), required=True, default=0.0)
    meters = fields.Float('Meters', default=0.0)
    length = fields.Float('Length (inch)', default=0.0)
    breadth = fields.Float('Breadth (inch)', default=0.0)
    height = fields.Float('Height (inch)', default=0.0)
    actual_weight = fields.Float('Actual Weight (kg)', default=0.0)
    vol_weight = fields.Float('Volume Weight', default=0.0)
    cft = fields.Float('CFT (cu ft)', default=0.0)
    missing_estimate_value = fields.Float('Missing Estimate Value', digits=(12, 2), default=0.0)
    material = fields.Text(string="Material")
    item_type = fields.Char(string="Item Type")
    purchase_code = fields.Char(string="Purchase Code")
    supplier = fields.Char(string="Supplier")
    standard_price = fields.Float(
        'Estimate Value', company_dependent=True, digits=(12, 2),
        groups="base.group_user",)
    list_price = fields.Float('Rental Price')
    default_code = fields.Char(string="Product Code")

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'
    _description = 'sale.order.line'

    item_code = fields.Char(string="Item Code")
    beta_quot_item_id = fields.Integer()

    @api.onchange('price_unit')
    def min_price(self):
        if self.order_id.below_min_price:
            return

        product_id = self.product_id
        unit_price = self.env['product.product'].search([('id', '=', product_id.id)], limit=1).list_price
        current_price = self.price_unit
        if current_price < unit_price:
            self.price_unit = self._origin.price_unit
            return {
                'warning': {'title': 'Warning',
                            'message': 'Current Price < Unit Price', },
            }
