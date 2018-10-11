
{
    'name': 'Customer Bill Mail',
    'version': '8.0.1.0.0',
    'category': 'Account',
    'author': 'Dedi Sinaga',
    'website': 'https://www.sicepat.com',
    'depends': [
        'base','sale','account','account_voucher','email_template','mail','sicepat_erp','report_xlsx',
    ],
    'data': [
        'workflows/account_voucher_wkf.xml',
        'datas/bill_payment_mail_template.xml',
        'datas/bill_invoice_mail_template_weekly.xml',
        'datas/bill_invoice_mail_template_monthly.xml',
        # 'datas/bill_overdue_mail_template.xml',
        'reports/bill_monthly_customer_reports.xml',
        'wizards/res_partner_wizard_print_report.xml',
        'wizards/res_partner_wizard_bill_mail.xml',
        'views/res_partner_view.xml',
    ],
    "installable": True,
}
