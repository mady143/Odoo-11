    # -*- coding: utf-8 -*-
from odoo import http
import json
class HrBiometric(http.Controller):
    @http.route('/hr_biometric/hr_biometric/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/hr_biometric/hr_biometric/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('hr_biometric.listing', {
        'root': '/hr_biometric/hr_biometric',
        'objects': http.request.env['hr_biometric.hr_biometric'].search([]),
        })

    @http.route('/hr_biometric/hr_biometric/objects/<model("hr_biometric.hr_biometric"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('hr_biometric.object', {
        'object': obj
        })
    

