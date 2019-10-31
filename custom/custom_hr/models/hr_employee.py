#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, date,timedelta
import calendar
import logging
import random
import re
from odoo.exceptions import ValidationError


class Shift(models.Model):
    _name = "employee.shifts"
    _description = "Employee_shift_timings"

    name = fields.Char('Shift Name', required=True)
    start_time = fields.Float('Start_time')
    end_time = fields.Float('End_time')




GENDER_SELECTION = [('male', 'Male'),
                    ('female', 'Female')]

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'
    shift = fields.Many2one('employee.shifts', 'Shift_Timings')
    #shift=  fields.Selection([("A", "Shift-1"), ("B", "Shift-2"), ("C", "Shift-3")], string="Work_Timings")
    emp_experience = fields.Char(string='Total Experience')
    emp_number = fields.Char(string='Employee Number', required=True)
   
    work_email = fields.Char('Work Email')
    blood_group = fields.Selection([
        ("A-positive", "A-positive"), ("A-negative", "A-negative"), ("B-positive", "B-positive"), ("B-negative", "B-negative"), ("AB-positive", "AB-positive"), ("AB-negative", "AB-negative"), ("O-positive", "O-positive"), ("O-negative", "O-negative")], string="Blood Group")
    is_manager = fields.Boolean(string="Is a Manager")

    pan_card = fields.Char(string='PAN Card No')
    aadhar_card = fields.Char(string='Aadhar Card Id')
    election_card = fields.Char(string='Election Card Id')
    driving_license = fields.Char(string='Driving License No')
    provident_fund = fields.Char(string='Provident Fund No')
    uan = fields.Char(string='UAN No')
    original_birthday = fields.Date("Original Date of Birth")
    place_of_birth = fields.Char("Place of Birth")
    address_permanent_id = fields.Many2one('res.partner', string='Permanent Address')
    biometric_login_id = fields.Char(string="Biometric Login ID")
    marriage_date = fields.Date("Marraige Date")
    date_of_joining = fields.Date("Date of Joining")
    primary_contact_name = fields.Char("Name")
    primary_contact_relation = fields.Char("Relation")
    primary_contact_no = fields.Char("Contact No")
    secondary_contact_name = fields.Char("Name")
    secondary_contact_relation = fields.Char("Relation")
    secondary_contact_no = fields.Char("Contact No")
    nominee_name = fields.Char("Name")
    nominee_dob = fields.Date("Date of Birth")
    nominee_relation = fields.Char("Relation")
    nominee_gender = fields.Selection(string='Gender',selection=GENDER_SELECTION)
    hide_tabs = fields.Boolean(compute='_compute_hide_tabs', string='Tabs hide')
    skype_id = fields.Char("Skype Id")
    uhid = fields.Char("UHID")
    spouse_uhid = fields.Char("Spouse's UHID")
    father_uhid = fields.Char("Father's UHID")
    mother_uhid = fields.Char("Mother's UHID")
    
    passport_id = fields.Char('Passport No', groups='base.group_user')
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account Number',
        domain="[('partner_id', '=', address_home_id)]", help='Employee bank salary account', groups='base.group_user')
    identification_id = fields.Char(string='Identification No', groups='base.group_user')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups='base.group_user')
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups='base.group_user')
    birthday = fields.Date('Date of Birth', groups='base.group_user')
    user_check_tick = fields.Boolean(default=False)
    work_random=fields.Char(string='test')
    birthday_random=fields.Char(string='test1')
    marriage_random=fields.Char(string='test2')
    work_exp=fields.Char(string='exp')
    employee_email_cc=fields.Char(string='email_cc')

    _sql_constraints = [
        ('email_uniq', 'unique (work_email)', "Email ID already exists !"),('emp_num_uniq', 'unique (emp_number)', "Employee number already exists !"),('emp_name_uniq', 'unique (name)', "Employee name already exists !")
    ]

    @api.onchange('work_phone','mobile_phone','primary_contact_no','secondary_contact_no' )
    def validate_phone(self):

        if self.work_phone:
           phone = self.work_phone
           match = re.match('^[0-9]{10}$', phone)
           if match == None:
            raise ValidationError('Not a valid work phone number ')
        if self.mobile_phone:
           phone = self.mobile_phone
           match = re.match('^[0-9]{10}$', phone)
           if match == None:
            raise ValidationError('Not a valid Phone number')
        if self.primary_contact_no:
           phone = self.primary_contact_no
           match = re.match('^[0-9]{10}$', phone)
           if match == None:
            raise ValidationError('Not a valid Phone number')
        if self.secondary_contact_no:
           phone = self.secondary_contact_no
           match = re.match('^[0-9]{10}$', phone)
           if match == None:
            raise ValidationError('Not a valid Phone number')

        
    @api.onchange('work_email')
    def email_validation(self):
      if self.work_email:
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.work_email)
        if match == None:
            raise ValidationError('Not a valid E-mail ID')
    @api.onchange('address_id')
    def _onchange_address(self):
        self.work_phone = self.address_id.phone
   
    @api.onchange('original_birthday','birthday')
    def validate_mail(self):
        datetime_from_string = fields.Date.from_string
        today = date.today()
        if self.original_birthday: 
           original_birthday = datetime_from_string(self.original_birthday)
           match = today-original_birthday
           if int(match.days/365) < 18:
             raise ValidationError('Not Eligible for work')
        if self.birthday: 
           birthday = datetime_from_string(self.birthday)
           match = today-birthday
           if int(match.days/365) < 18:
              raise ValidationError('Not Eligible for work')
   
    def employee_user(self):
         #if self.parent_id:
         parent_id_record = self.env['hr.employee'].search([('id', '=', self.parent_id.id)])
         parent_resource_id = self.env['resource.resource'].search([('id', '=', parent_id_record.resource_id.id)])
         user_ids = self.env['res.users'].search([('id', '=', parent_resource_id.user_id.id)])         
         if self.user_id and self.parent_id.id:
             users = self.env['res.users'].search([('id', '=', self.user_id.id)])
             users.write({'parent_id': user_ids.id})
    @api.onchange('parent_id')
    def _update_parent_id(self):
        if self.user_id:
           self.user_check_tick = True
           self.employee_user()
    # To create parent_id field in res_users tables based on selected related user in employee HR_settings form
    @api.onchange('user_id')
    def _update_parent_id_emp_form(self):
        self.employee_user()

    def onchange_name_email(self):
        if self.user_id:
            if self.parent_id:
             self.env.cr.execute('update res_users set parent_id=%s where id=%s', (self.parent_id.resource_id.user_id.id, self.user_id.id))
            else:
             self.env.cr.execute('update res_users set parent_id=%s where id=%s', (None, self.user_id.id))
       
        employee_names = self.env['hr.employee'].search([('name', '=', self.name),('id', '!=', self.id)])
        if employee_names:
            raise ValidationError('Employee name already exits!!!')
        if self.user_id:
            self.env.cr.execute('update res_partner set name=%s where id=%s', (self.name, self.user_id.partner_id.id))
        
        employee_emails = self.env['hr.employee'].search([('work_email', '=', self.work_email),('id', '!=', self.id)])  
        if employee_emails:
            raise ValidationError('Employee email already exits!!!') 
        if self.user_id:
            self.env.cr.execute('update res_users set login=%s where id=%s', (self.work_email, self.user_id.id))
            self.env.cr.execute('update res_partner set email=%s where id=%s', (self.work_email, self.user_id.partner_id.id))
            

    # To create parent_id field in res_users tables based on clicking the user creation button in employee form
    @api.multi
    def create_user(self):
        user_id = self.env['res.users'].create({'name': self.name,'login': self.work_email})
        self.address_home_id = user_id.partner_id.id
        self.user_check_tick = True
        self.user_id = user_id.id
        self.env.cr.execute('update res_partner set email=%s where id=%s', (self.work_email, user_id.partner_id.id))
        if self.user_id:
           self.employee_user()
    @api.model
    def create(self,values):
        create_employee = super(HrEmployee, self).create(values)
        new_user = self.env['res.users'].create({'name': create_employee.name, 'login':create_employee.work_email})
        create_employee.address_home_id = new_user.partner_id.id
        create_employee.user_id = new_user.id
        self.env.cr.execute('update res_partner set email=%s where id=%s', (create_employee.work_email, new_user.partner_id.id))
        # template = self.env.ref('auth_signup.reset_password_email')
        # self.env['mail.template'].browse(template.id).send_mail(new_user.id, force_send=False)
        return create_employee
       

    @api.onchange('address_home_id')
    def user_checking(self):
        if self.address_home_id and self.user_id:
            self.user_check_tick = True
        else:
            self.user_check_tick = False

    @api.multi
    def _compute_hide_tabs(self):
        res = {}
        for employee in self:
            if self.env.user.has_group('launchship_hr.group_hr_ceo'):
                employee.hide_tabs = False
            elif self._context.get('uid') == employee.user_id.id:
                employee.hide_tabs = False
            else:
                employee.hide_tabs = True

    def email_cc1(self,work_email):
            self._cr.execute("select work_email from hr_employee")
            res_all = self.env.cr.fetchall()
            email_cc=','.join(key[0] for key in res_all if key[0]!=work_email)
            return(email_cc)

    @api.multi
    def send_birthday_email(self):
        ir_data = self.env['ir.model.data']
        wish_template = ir_data.get_object('launchship_hr', 'email_template_emp_birthday_wish')
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        for emp in self.search([('original_birthday', 'like', today_month_day)]):
            emp.birthday_random=str(random.randrange(1,10,1))
            emp.employee_email_cc=self.email_cc1(emp.work_email)
            wish_template.sudo().send_mail(emp.id, force_send=False)
        return None
     
    @api.multi
    def send_work_anniversary_email(self):
        ir_data = self.env['ir.model.data']
        wish_template = ir_data.get_object('launchship_hr', 'email_template_emp_work_anniversary_wish')
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        for emp in self.search([('date_of_joining', 'like', today_month_day)]):
            date = datetime.strptime(emp.date_of_joining,'%Y-%m-%d')
            emp.work_exp=str(int(today.strftime('%Y'))-int(date.strftime('%Y')))
            if int(emp.work_exp) >0:
             emp.work_random=str(random.randrange(1,6,1))
             emp.employee_email_cc=self.email_cc1(emp.work_email)
             wish_template.sudo().send_mail(emp.id, force_send=False)
        return None
        
    @api.multi
    def send_mrg_anniversary_email(self):
        ir_data = self.env['ir.model.data']
        wish_template = ir_data.get_object('launchship_hr', 'email_template_emp_mrg_anniversary_wish')
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        for emp in self.search([('marriage_date', 'like', today_month_day)]):
            emp.marriage_random=str(random.randrange(1,6,1))
            emp.employee_email_cc=self.email_cc1(emp.work_email)
            wish_template.sudo().send_mail(emp.id, force_send=False)
        return None
    
    @api.multi
    def add_leaves_every_monthend(self):
        employee = self.env['hr.employee']
        hr_holidays = self.env['hr.holidays']
        leagale_leave_id = self.env.ref('hr_holidays.holiday_status_cl').id
        
        today_date = date.today()
        datetime_from_string = fields.Date.from_string
        
        for emp in employee.search([]):
           joining_date = datetime_from_string(emp.date_of_joining)
           if joining_date and today_date>=joining_date:
                           
            dic = {}
            dic['name'] = "Legal Leaves for "+emp.name
            dic['holiday_status_id'] = leagale_leave_id
            dic['type'] = "add"
            dic['number_of_days_temp'] = 1.75
            dic['employee_id'] = emp.id
            dic['system_generated'] = True
            dic['allottedOn'] = allottedOn = str(today_date.month)+str(today_date.year)
            
            if joining_date and (joining_date.year==today_date.year and joining_date.month==today_date.month):
                no_of_days_month = calendar.monthrange(today_date.year,today_date.month)[1]
                remaing_days_in_month=no_of_days_month-joining_date.day
                first_date = datetime(today_date.year, today_date.month, 1)
                last_date = datetime(today_date.year, today_date.month, no_of_days_month)# first import timedelta 
                joining__date=datetime(today_date.year, today_date.month, joining_date.day)
                no_of_working_days_month= no_of_days_month-self.get_special_days(first_date, last_date, emp)
                remaing_working_days_in_month=remaing_days_in_month-self.get_special_days(joining__date, last_date, emp)                 
                dic['number_of_days_temp'] = (remaing_working_days_in_month+1)*1.75/no_of_working_days_month
            
            domain = [('holiday_status_id', '=', leagale_leave_id),('type', '=', 'add'),
                                   ('allottedOn', '=', allottedOn),('employee_id', '=', emp.id),('system_generated','=',True)]
            hr_holidays_obj = hr_holidays.search(domain)
            if hr_holidays_obj:
                continue
            #    holiday_id = hr_holidays_obj.id
            #    number_of_days_temp = hr_holidays_obj.number_of_days_temp+1.75
            #    hr_holidays_obj.update({'number_of_days_temp':number_of_days_temp})
            #else:
            dic['state'] = 'validate'
            holiday_id = hr_holidays.create(dic)
            self._cr.commit() 
            #holiday_id.action_approve()
    
    @api.multi
    def write(self, values):   
        xx=super(HrEmployee, self).write(values)
        self.onchange_name_email()
        return xx


    def get_special_days(self, date_from, date_to, employee):   
        public_leave_ids = self.env['hr.holidays.public.line'].search([
            ('state_ids', 'in', employee.company_id.state_id.id)])
        special_days = 0
        for date in self.daterange(date_from, date_to):
            date_str = str(date.date())
            public_leave = public_leave_ids.filtered(
                lambda r: r.date == date_str)
            weeks = {'monday': 'Monday' ,'tuesday' : 'Tuesday', 'wednesday': 'Wednesday', 'thursday' : 'Thursday', 'friday' : 'Friday', 'saturday' : 'Saturday','sunday' : 'Sunday'}
            second_week_off=employee.address_id.second_week_off
            first_week_off=employee.address_id.first_week_off
            if public_leave:
                special_days = special_days+1
            elif first_week_off and date.strftime("%A") == weeks[first_week_off] :
                special_days = special_days+1
            elif second_week_off and date.strftime("%A") == weeks[second_week_off]:
                special_days = special_days+1
        return special_days           
            
    def daterange(self, date_from, date_to):
        for n in range(int((date_to - date_from).days) + 1):
            yield date_from + timedelta(n) 
