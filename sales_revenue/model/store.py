# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ResStore(models.Model):
    _name = "res.store"
    _description = "Stores"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
