import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw


class report_bank_statement(report_sxw.rml_parse):

    def set_context(self, objects, data, ids, report_type=None):
        res = super(report_bank_statement, self).set_context(objects, data, ids, report_type=report_type)
        
        bank_st = self.pool.get('account.bank.statement')
        
        context = {'lang': self.pool.get('res.users').browse(self.cr, self.uid, self.uid).lang}
        state_field = bank_st.fields_get(self.cr, self.uid, 'state', context=context)['state']['selection']
        state_dict = {}
        for state_tuple in state_field:
            state_dict[state_tuple[0]] = state_tuple[1]

        bank_st_info = {}
        statements = bank_st.search(self.cr, self.uid, [('id', 'in', ids)], order="journal_id, state, date")
        for statement in bank_st.browse(self.cr, self.uid, statements):
            key = statement.journal_id.name + '-' + statement.name + '-' + statement.date
            for st_line in statement.line_ids:
                if bank_st_info.get(key):
                    bank_st_info[key]['lines'] += st_line
                    bank_st_info[key]['total_amount'] += -1*st_line.amount
                else:
                    bank_st_info[key] = {
                            'voucher_name': statement.name, 
                            'voucher_date': statement.date, 
                            'journal_name': statement.journal_id.name, 
                            'currency': statement.journal_id.currency, 
                            'total_amount': -1*st_line.amount, 
                            'lines': st_line,
                            'state': state_dict[statement.state],
                        }

        # Qweb for-each do not work on dict, so we send a list and we sort it by the name of the employee
        # that way if we have two sheet for the same employee they will follow in the report
        self.localcontext.update({
            'get_statements': lambda : [v for k,v in sorted(bank_st_info.items())],
            })
        return res


class report_bank_voucher(osv.AbstractModel):
    _name = 'report.bank_voucher_report.report_bank_statement'
    _inherit = 'report.abstract_report'
    _template = 'bank_voucher_report.report_bank_statement'
    _wrapped_report_class = report_bank_statement
