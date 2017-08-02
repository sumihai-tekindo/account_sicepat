try:
    from . import models
    from . import report
except ImportError:
    import logging
    logging.getLogger('openerp.module').warning('''report_xlsx not available in
    addons path. report_balance_sheet_custom will not be usable''')
