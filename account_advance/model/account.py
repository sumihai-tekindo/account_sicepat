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

from openerp.osv import fields, osv

class account_chart_template(osv.osv):
    _inherit='account.chart.template'

    _columns={
        'property_account_advance_receivable': fields.many2one('account.account.template', 'Receivable Advance Account'),
        'property_account_advance_payable': fields.many2one('account.account.template', 'Payable Advance Account'),
    }

class wizard_multi_charts_accounts(osv.osv_memory):
    _inherit='wizard.multi.charts.accounts'

    def generate_properties(self, cr, uid, chart_template_id, acc_template_ref, company_id, context=None):
        """
        This method used for creating properties.

        :param chart_template_id: id of the current chart template for which we need to create properties
        :param acc_template_ref: Mapping between ids of account templates and real accounts created from them
        :param company_id: company_id selected from wizard.multi.charts.accounts.
        :returns: True
        """
        res = super(wizard_multi_charts_accounts, self).generate_properties(cr, uid, chart_template_id, acc_template_ref, company_id, context=context)
        property_obj = self.pool.get('ir.property')
        field_obj = self.pool.get('ir.model.fields')
        todo_list = [
            ('property_account_advance_receivable','res.partner','account.account'),
            ('property_account_advance_payable','res.partner','account.account'),
        ]
        template = self.pool.get('account.chart.template').browse(cr, uid, chart_template_id, context=context)
        for record in todo_list:
            account = getattr(template, record[0])
            value = account and 'account.account,' + str(acc_template_ref[account.id]) or False
            if value:
                field = field_obj.search(cr, uid, [('name', '=', record[0]),('model', '=', record[1]),('relation', '=', record[2])], context=context)
                vals = {
                    'name': record[0],
                    'company_id': company_id,
                    'fields_id': field[0],
                    'value': value,
                }
                property_ids = property_obj.search(cr, uid, [('name','=', record[0]),('company_id', '=', company_id)], context=context)
                if property_ids:
                    #the property exist: modify it
                    property_obj.write(cr, uid, property_ids, vals, context=context)
                else:
                    #create the property
                    property_obj.create(cr, uid, vals, context=context)
        return res
