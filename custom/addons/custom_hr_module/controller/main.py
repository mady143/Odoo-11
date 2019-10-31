# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import http
from odoo.addons.web.controllers.main import Database

class Dbtest(Database):
    @http.route('/launchship_dbmanager', type='http', auth='user')
    def manager(self, **kw):
        return super(Dbtest, self).manager(**kw)


