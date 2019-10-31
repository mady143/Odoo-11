# -*- coding: utf-8 -*-
# Copyright 2015-17 Eficent Business and IT Consulting Services S.L.
#     (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

_WEEKDAYS = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday')
]


class ResCompany(models.Model):
    _inherit = 'res.partner'

    first_week_off = fields.Selection(
        _WEEKDAYS, string='First Week Day')
    second_week_off = fields.Selection(
        _WEEKDAYS, string='Second Week Day')
