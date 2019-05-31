# -*- coding: utf-8 -*-

from odoo import models, fields, api

class students(models.Model):
    _name = 'students.students'


    @api.multi
    def button_done(self):
        for rec in self:
            rec.write({'status': 'done'})

    @api.multi
    def button_reset(self):
        for rec in self:
            rec.write({'status': 'draft'})

    @api.multi
    def button_cancel(self):
        for rec in self:
            rec.write({'status': 'cancel'})

    name = fields.Char(string="Name",required=True)
    age  = fields.Integer(string="Age")
    photo = fields.Binary(string='Image')
    mobile = fields.Char(string="Work Mobile")
    email  = fields.Char(string="Email")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')], string='Gender')
    student_dob = fields.Date(string="Date of Birth")
    blood_group = fields.Selection([('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],string='Blood Group')
    nationality = fields.Many2one('res.country', string='Nationality')
    country_id  = fields.Many2one('res.country', string='Country' ,required=True)
    state_id    = fields.Many2one('res.country.state', string='State')
    city_id     = fields.Char(string='City')
    state = fields.Char(string= "Other State")
    hide = fields.Boolean(string='Hide')
    student_type = fields.Many2one('students.type')
    status = fields.Selection([('draft','Draft'),('done','Done'),('cnacel','Canceled')],default="draft")
    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            l=[]
            for country in self.country_id:
                l.append(country.id)

            if(self.env['res.country.state'].search([('country_id', '=', l)])):
                self.hide = False
                self.state=''
                self.state_id=[]
            else:
                self.hide = True
                self.state=''
            return {'domain': {'state_id': [('country_id', '=', l )]}}
        else:
            self.hide = True
            self.state=''
            return {'domain': {'state_id': []}}



    # @api.onchange('country_id')
    # def _onchange_country_id(self):
    #     if self.country_id:
    #         if(self.env['res.country.state'].search([('country_id', '=', self.country_id.id)])):
    #             self.hello=True
    #             self.hide = True
    #         else:
    #             self.hello=False
    #             self.hide = False
    #         return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
    #     else:
    #         return {'domain': {'state_id': []}}
    

    @api.depends('state_id')
    def new_state(self):
        if self.state_id:
            self.state = self.state_id.name



class City(models.Model):
	_name = 'res.country.state.city'
	_description = 'City'
	_order = 'name'

	name = fields.Char("Name", required=True, translate=True)
	zipcode = fields.Char("Zip")
	country_id = fields.Many2one('res.country', string='Country', required=True)
	state_id = fields.Many2one(
	'res.country.state', 'State', domain="[('country_id', '=', country_id)]")

class Students_Type(models.Model):
    _name = 'students.type'
    _description = 'Students_Type'
    _order = 'name'

    name = fields.Char("Name", required=True, translate=True)
    
