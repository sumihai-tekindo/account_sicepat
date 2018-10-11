
import datetime
from lxml import etree
import math
import pytz
import urlparse

import openerp
from openerp import tools, api
from openerp.osv import osv, fields
from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _
from openerp.addons.base.res.res_partner import format_address



class res_partner(osv.Model, format_address):
	_description = 'Partner'
	_inherit = "res.partner"

	_columns = {
		'grade_type_id'	: fields.many2one("master.cust.grade.type","Grade Type"),
		'class_id'		: fields.many2one("master.cust.grade","Customer Grade"),
		'masterdata_id'	: fields.integer("Master Data ID"),
	}