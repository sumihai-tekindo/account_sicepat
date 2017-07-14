from openerp.osv import osv
from openerp.tools.translate import _

class cashback_customer_refund(osv.osv_memory):
    """
    This wizard will approve the all the selected submit or acknowledge invoices
    """

    _name = "cashback.customer.refund"
    _description = "Generate Customer Refund"

    # def generate_customer_refund(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     proxy = self.pool['account.invoice']
    #     active_ids = context.get('active_ids', []) or []

    #     if not self.pool['res.users'].has_group(cr, uid, 'invoice_supplier_validate.group_approve_invoices'):
    #         raise osv.except_osv(_('Warning!'), _("You don't have access to approve the selected invoice(s)."))
        
    #     for record in proxy.browse(cr, uid, active_ids, context=context):
    #         if record.state not in ('submit', 'acknowledge'):
    #             raise osv.except_osv(_('Warning!'), _("Selected invoice(s) cannot be approve as they are not in 'Submit' or 'Acknowledge' state."))
    #         record.signal_workflow('invoice_approve')
    #     return {'type': 'ir.actions.act_window_close'}



class cashback_submit(osv.osv_memory):

    _name = "cashback.submit"


    def cashback_submit_wizard(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        proxy = self.pool['account.cashback.line']
        active_ids = context.get('active_ids', []) or []

        if not self.pool['res.users'].has_group(cr, uid, 'account_cash_back.group_submit_cashback'):
            raise osv.except_osv(_('Warning!'), _("You don't have access to submit the selected cashback(s)."))
        
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('draft'):
                raise osv.except_osv(_('Warning!'), _("Selected cashback(s) cannot be approve as they are not in 'Draft' state."))
            record.button_submit()
        return {'type': 'ir.actions.act_window_close'}



class cashback_approve(osv.osv_memory):

    _name = "cashback.approve"


    def cashback_approve_wizard(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        proxy = self.pool['account.cashback.line']
        active_ids = context.get('active_ids', []) or []

        if not self.pool['res.users'].has_group(cr, uid, 'account_cash_back.group_approve_cashback'):
            raise osv.except_osv(_('Warning!'), _("You don't have access to approve the selected cashback(s)."))
        
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('submitted'):
                raise osv.except_osv(_('Warning!'), _("Selected cashback(s) cannot be approve as they are not in 'Submit' state."))
            record.button_approve()
        return {'type': 'ir.actions.act_window_close'}