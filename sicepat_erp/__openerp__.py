# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Pambudi Satria (<https://github.com/pambudisatria>).
#    @author Pambudi Satria <pambudi.satria@yahoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Sicepat Ekspres",

    'summary': """
        Sicepat Ekspres Localization
    """,

    'description': """
=====================================
Odoo Localization for Sicepat Ekspres
=====================================

Sicepat Ekpres is a expedition company located in West Jakarta, Indonesia.
This module add some feature to complete Sicepat Ekspres bussiness process.

Feature
-------

    """,

    'author': "Pambudi Satria",
    'website': "https://github.com/pambudisatria",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'sequence': 1,
    'version': '8.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account_followup',
        'account_accountant',
        'invoice_line_comment',
        'account_invoice_revision',
        'invoice_send_mail',
        'invoice_filter_date',
        'account_advance',
        'email_template_dateutil',
        'mail_delete_sent_by_footer',
        'disable_invoice_editable_list',
        'l10n_id_sicepat',
        'disable_openerp_online',
        'base_concurrency',
        'base_setup',
        'web_sheet_full_width',
        'web_groupby_expand',
        'web_export_view',
        'l10n_id_country_state',
        'report',
        'web',
    ],

    # always loaded
    'data': [
        'data/res_company.xml',
        'data/res_groups.xml',
        'data/payment_term.xml',
#         'data/account.analytic.account.csv',
        'data/analytic_account.xml',
        'data/report_paperformat.xml',
        'data/cron_job.xml',
#         'wizard/sicepat_erp_wizard.yml',
        'wizard/account_report_partner_outstanding_view.xml',
        'invoice_partner_bank2/invoice_partner_bank2_view.xml',
        'invoice_line_dest_code/invoice_line_dest_code_view.xml',
        'invoice_line_recipient/invoice_line_recipient_view.xml',
        'invoice_line_jne_number/invoice_line_jne_number_view.xml',
        'invoice_line_exp_cost/invoice_line_exp_cost_view.xml',
        'views/ir_sequence_view.xml',
        'views/account_invoice_view.xml',
        'views/voucher_payment_receipt_view.xml',
        'views/res_config_view.xml',
        'views/layouts.xml',
#         'views/report_invoice_old.xml',
        'views/report_invoice.xml',
        'views/report_partner_outstanding.xml',
        'edi/invoice_action_data.xml',
        'views/sicepat_template.xml',
        'security/ir.model.access.csv',
    ],

    # only loaded in demonstration mode
    'demo': [
    ],

    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}