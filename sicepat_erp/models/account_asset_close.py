from openerp.osv import osv
from openerp.tools.translate import _

class account_asset_close(osv.osv_memory):
    """
    This wizard will submit the all the selected draft invoices
    """

    _name = "account.asset.close"
    _description = "Close the selected assets"

    def asset_close(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []
        
        proxy = self.pool['account.asset.asset']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('open'):
                raise osv.except_osv(_('Warning!'), _("Selected asset(s) cannot be closed as they are not in 'Running' state."))
            record.set_to_close()
            
        return {'type': 'ir.actions.act_window_close'}