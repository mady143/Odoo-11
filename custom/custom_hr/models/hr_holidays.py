#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import math
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.tools import float_compare
from odoo.tools.translate import _
from odoo import http
import pytz
import logging
import re
from odoo.exceptions import ValidationError

HOURS_PER_DAY = 8

class res_users(models.Model):

   _inherit = 'res.users'

   parent_id = fields.Many2one('res.users', string='Parent ID')

   def onchange_user_name_email(self):
     parent_id_record = self.env['res.partner'].search([('name', '=', self.name),('id', '!=', self.partner_id.id)])
     if parent_id_record:
      raise ValidationError('User name already exits!!!')
     parent_resource_id = self.env['resource.resource'].search([('user_id', '=', self.id)])
     if parent_resource_id:
      self.env.cr.execute('update hr_employee set name=%s where resource_id=%s', (self.name, parent_resource_id.id))
  
     unique_email = self.env['res.users'].search([('login', '=', self.login),('id', '!=', self.id)])
     if unique_email:
      raise ValidationError('User email already exits!!!')
     parent_resource_id = self.env['resource.resource'].search([('user_id', '=', self.id)])
     if parent_resource_id:
      self.env.cr.execute('update hr_employee set work_email=%s where resource_id=%s', (self.login, parent_resource_id.id))
    
   @api.multi
   def write(self, values):   
        xx=super(Users, self).write(values)
        self.onchange_user_name_email()
        return xx

   
   @api.onchange('login')
   def _email_validate(self):
      if self.login:
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.login)
        if match == None:
            raise ValidationError('Not a valid E-mail ID')

class res_partners(models.Model):
     _inherit = 'res.partner'

     @api.onchange('email')
     def email_validation(self):
       if self.email:
          match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
          if match == None:
            raise ValidationError('Not a valid E-mail ID')
     @api.onchange('phone', 'mobile')
     def phone_validation(self):
        if self.phone:
           phone = self.phone

           match = re.match('^[0-9]{10}$', phone)
           if match == None:
            raise ValidationError('Not a valid Phone number')
        if self.mobile:
           phone = self.mobile
           match = re.match('^[0-9]{10}$', phone)
           if match == None:
            raise ValidationError('Not a valid Mobile number')
class HolidaysType(models.Model):

    _inherit = "hr.holidays.status"
    """
    iswfh = fields.Boolean(string="Is WFH ?", help="Tick the box if this leave type is a work from home, so that it will not be visible in leave summury")"""

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        action_id = http.request.session.get('action')
        legal_leave_id = self.env.ref('hr_holidays.holiday_status_cl').id
        menu_ids_records = self.env['ir.ui.menu'].search(['|',('name', '=', 'Allocation Request'),('name','=','Leaves Allocation')])
        menu_ids = []
        for menu in menu_ids_records:
            menu_ids.append(menu.action.id)
        if action_id in menu_ids:
           args = [['id', '!=', legal_leave_id]]
        res = super(HolidaysType, self).name_search(name='', args=None, operator='!=', limit=100)
        ids = self.search(args , limit=limit)
        if ids:
           return ids.name_get()
        return res

class Holidays(models.Model):
    _inherit = 'hr.holidays'
    _description = 'Leave'
 
    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
            help="The status is set to 'To Submit', when a holiday request is created." +
            "\nThe status is 'To Approve', when holiday request is confirmed by user." +
            "\nThe status is 'Refused', when holiday request is refused by manager." +
            "\nThe status is 'Approved', when holiday request is approved by manager.")
    name = fields.Char('Description', required=True)
    email_cc = fields.Char('Emails CC', help="Specify email addresses separated by comma, if this has to intimate others too.")
    email_cc1 = fields.Many2many('hr.employee', string='Emails CC')
    system_generated = fields.Boolean("Is a System Generated Allocation Request")
    allottedOn = fields.Char('LeavesAllottedDate')
    holiday_status_id = fields.Many2one("hr.holidays.status", string="Leave Type", required=True, readonly=True,
    states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days_temp = fields.Float(
    'Allocation', copy=False, readonly=True,
    states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
    help='Number of days of the leave request according to your working schedule.')
    hide = fields.Boolean(string='Hide', default=True)
    test = fields.Float('test')
    hide1 = fields.Boolean(string='Hide', default=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, default=_default_employee, track_visibility='onchange')
    holiday_type = fields.Selection([
        ('employee', 'By Employee')
    ], string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category')
    admin_email= fields.Char(string='admin_email', compute='_find_admin_email')

    def _find_admin_email(self):
       admin_details=self.env['res.users'].search([('id', '=', 1)]) 
       self.admin_email=admin_details.login 


    @api.onchange('date_from')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """

        action_dict = http.request.params['args'][4]['params']
        if action_dict:
          http.request.session['action'] = action_dict['action']
        #self.employee_shifts()
        self._local_to_UTC_timezone()
        date_from = self.date_from
        date_to = self.date_to

        date_from_user_tz = self.change_to_user_tz(self.date_from)
        date_to_user_tz = self.change_to_user_tz(self.date_to)

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
            self.compute_days(number_of_days_temp , date_from_user_tz, date_to_user_tz)
            #self.compute_days(self._get_round(number_of_days_temp), date_from_user_tz, date_to_user_tz)
            #self.number_of_days_temp =self._get_round(number_of_days_temp)
        else:
            self.number_of_days_temp = 0

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to

        date_from_user_tz = self.change_to_user_tz(self.date_from)
        date_to_user_tz = self.change_to_user_tz(self.date_to)
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
            #self.number_of_days_temp = self._get_round(number_of_days_temp)
            self.compute_days(number_of_days_temp , date_from_user_tz, date_to_user_tz)
        else:
            self.number_of_days_temp = 0
    
    def _local_to_UTC_timezone(self):      
        if type(self.date_from)==str and self.hide1==True:
         date = datetime.strptime(self.date_from,'%Y-%m-%d %H:%M:%S')
         self.date_from=str(date.replace(minute=30, hour=3, second=00))
         self.date_to=str(fields.Datetime.from_string(self.date_from) + timedelta(hours=HOURS_PER_DAY))
         self.hide1=False  

    @api.onchange('employee_id',)
    def hello(self):
        self.hide1=True

    #@api.onchange('employee_id')
    def employee_shifts(self):
      if self.hide1==True:
       employee_shift=self.employee_id.shift
       date = datetime.strptime(self.date_from,'%Y-%m-%d %H:%M:%S')
       date1 = datetime.strptime(self.date_to,'%Y-%m-%d %H:%M:%S')
       local = pytz.timezone ('Asia/Kolkata')

       if employee_shift=='A':
          date=date.replace(minute=00, hour=1, second=00)
          date1=date1.replace(minute=00, hour=9, second=00)
       elif employee_shift=='C':
           date=date.replace(minute=00, hour=17, second=00)
           date1=date1.replace(minute=00, hour=1, second=00)
       else:
           date=date.replace(minute=00, hour=9, second=00)
           date1=date1.replace(minute=00, hour=17, second=00)
 

       local_dt = local.localize(date, is_dst=None)
       utc_dt = local_dt.astimezone(pytz.utc)
       self.date_from=utc_dt.strftime ("%Y-%m-%d %H:%M:%S")
       local_dt1 = local.localize(date1, is_dst=None)
       utc_dt1 = local_dt1.astimezone(pytz.utc)
       self.date_to=utc_dt1.strftime ("%Y-%m-%d %H:%M:%S")
       #self.date_to=str(fields.Datetime.from_string(self.date_from) + timedelta(hours=HOURS_PER_DAY))
       self.hide1=False

    def _get_round(self, value):
        value_list = str(value).split(".")
        if len(value_list) == 2:
            if 0 < float("0."+value_list[1]) <= 0.5:
               return int(value_list[0])+0.5
            elif 0.5 < float("0."+value_list[1]) <= 1:
               return int(value_list[0])+1
            else:
               return value
        else:
           
           return value
            
    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)
        time_delta = to_dt - from_dt
        
        time_delta_hours=time_delta.seconds/(60*60)
        if time_delta_hours>(HOURS_PER_DAY/2):
          time_delta_hours=float(1)
        else:
          time_delta_hours=float(0.5)
        return (time_delta.days + time_delta_hours)
 
    @api.multi         
    def _onchange_number_of_days_temp(self):
         if float(self.test) != float(self.number_of_days_temp) and self.type=='remove':
             raise ValidationError(_("The Number of days doesn't fit for days")) 
         if float(self.test) == float(self.number_of_days_temp) and float(self.number_of_days_temp)==float(0) and self.type=='remove':
             raise ValidationError(_("You are trying to apply leave on holidays/weekdays")) 
         if float(self.number_of_days_temp)==float(0) and self.type=='add':
             raise ValidationError(_("You can't apply request for Zero(0) days"))   

    # Show and Hide Approve button based on Employee_id
    #@api.multi
    #@api.onchange('employee_id')
    def _compute_hide(self):
      #  show the Approve button for CEO group 
      if self.env.user.has_group('launchship_hr.group_hr_holidays_ceo1'): 
       self.hide = True
      else:
       #  show the approve button for childeren of login user 
       if self.employee_id.parent_id.user_id.id==self.env.uid or self.employee_id.parent_id.parent_id.user_id.id==self.env.uid:
          self.hide = True
       else:
          self.hide = False  



    @api.model
    def search1234(self, args, offset=0, limit=None, order=None, count=False):
        # TDE FIXME: strange
        if self.env.user.has_group('hr_induction.group_dept_manager'):

            if ('search_default_department' in self._context.keys()):
                args.append((('employee_id.parent_id.user_id.id', '=', self._context['uid'])))
            elif ('search_default_my_leaves' in self._context.keys()):
                args.append((('employee_id.user_id.id', '=', self._context['uid'])))
        return super(Holidays, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.multi
    def get_wfm_days(self, employee_id):
        
        date_from = fields.Datetime.from_string(self.date_from)
        today_month = '%-' + date_from.strftime('%m') + '-%' 
        holidays = self.env['hr.holidays'].search([
            ('employee_id', '=', employee_id.id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', '=', self.holiday_status_id.id),
            ('date_from','like',today_month)
        ])
        no_of_days = 0
        for holiday in holidays:
            no_of_days += holiday.number_of_days_temp
        return no_of_days

    @api.multi
    def action_approve(self):
        # email_cc code###############################
        employee_leaves_count = self.env['hr.employee'].search([])
        for emp_leaves_count in employee_leaves_count:
          update_leaves=emp_leaves_count.leaves_count
        leaves_count = self.env['hr.employee'].search([('remaining_leaves', '!=', update_leaves)])
        if leaves_count:
          self.state = 'confirm'

        if 1==1:
           ll=[]
           if self.employee_id.id:
              ll.append(self.employee_id.id)
           if self.employee_id.parent_id.id:
              ll.append(self.employee_id.parent_id.id) 
           ll=tuple(ll)
           if ll:
            self._cr.execute("select work_email from hr_employee where parent_id in %s", (ll,))
            res_all = self.env.cr.fetchall()
            self.email_cc=', '.join(key[0] for key in res_all if key[0]!=self.employee_id.work_email)
            if self.employee_id.parent_id.id and self.email_cc:
                 self.email_cc=self.email_cc+', '+self.employee_id.parent_id.work_email
            elif self.employee_id.parent_id.id:
                 self.email_cc=self.employee_id.parent_id.work_email
            for h in self.email_cc1:
                 if h.work_email not in self.email_cc and self.email_cc: 
                  self.email_cc=self.email_cc+', '+h.work_email 
                 elif h.work_email not in self.email_cc:
                  self.email_cc=h.work_email 

        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))


        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            ################Customized for Work from home##############
            '''leave_status_id = self.holiday_status_id.id
            workfromhomerefid = self.env.ref('launchship_hr.holiday_status_workfromhome').id
            
            if (leave_status_id == workfromhomerefid):
                days_in_month = self.get_wfm_days(self.employee_id)
                if days_in_month > 2:
                    return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})'''
            ##################Customized for Work from home#############
            if holiday.state != 'confirm':
                raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            else:
                holiday.action_validate()

    #Inherited following functions to send emails when a action on leave       
    @api.multi
    def action_confirm(self):  
        ################Customized for Work from home##############
        '''for holiday in self:
            leave_status_id = self.holiday_status_id.id
            workfromhomerefid = self.env.ref('launchship_hr.holiday_status_workfromhome').id

            if (leave_status_id == workfromhomerefid) and holiday.number_of_days_temp>1:
                raise UserError(_('You can apply only one Work From Home request at a time.'))'''
        ###########################################################

        res = super(Holidays, self).action_confirm()
        ir_model_data = self.env['ir.model.data']
        if self.type == 'remove':
            template_id = ir_model_data.get_object_reference('launchship_hr', 'email_template_leave_request')[1]
        if self.type == 'add':
            template_id = ir_model_data.get_object_reference('launchship_hr', 'email_template_leave_allocation_request')[1]
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=False)
        return res
    
    @api.multi    
    def action_validate(self):
        res = super(Holidays, self).action_validate()
        ir_model_data = self.env['ir.model.data']
        if self.type == 'remove':

            #Adding Attendance Records for WFH
            '''leave_status_id = self.holiday_status_id.id
            workfromhomerefid = self.env.ref('launchship_hr.holiday_status_workfromhome').id
            if leave_status_id == workfromhomerefid:
                attendance = self.env['hr.attendance']
                vals = {
                'employee_id': self.employee_id.id,
                'check_in': self.date_from,
                'check_out': self.date_to
                }
                attendance.create(vals)'''
            ########################################

            template_id = ir_model_data.get_object_reference('launchship_hr', 'email_template_leave')[1]
        if self.type == 'add':
            template_id = ir_model_data.get_object_reference('launchship_hr', 'email_template_leave_allocation_approval')[1]
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=False)
        return res
    
    @api.multi
    def action_refuse(self):
        ir_model_data = self.env['ir.model.data']
        if self.employee_id:
         if self.type == 'remove'  and self.type:
            template_id = ir_model_data.get_object_reference('launchship_hr', 'email_template_leave_rejection')[1]
         if self.type == 'add' and self.type:
            template_id = ir_model_data.get_object_reference('launchship_hr', 'email_template_leave_allocation_rejection')[1]
         self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=False)
        res = super(Holidays, self).action_refuse()
        return res


    @api.model
    def create(self, values):
        xx=super(Holidays, self).create(values)
        if len(self)==1:
          self._onchange_number_of_days_temp()
        return xx


    @api.multi
    def write(self, values):   
        xx=super(Holidays, self).write(values)
        if len(self)==1:
         self._onchange_number_of_days_temp()
        return xx


    def change_to_user_tz(self, date):
        """
        Take date and return it in the user timezone
        :param date:
        :return:
        """
        if not date:
            return False
        date_object = datetime.strptime(date,
                                        tools.DEFAULT_SERVER_DATETIME_FORMAT)
        date_user_tz = fields.Datetime.context_timestamp(self.sudo(self._uid),
                                                         date_object)
        date_user_tz_string = date_user_tz.strftime(DTF)
        return date_user_tz_string

    def daterange(self, date_from, date_to):
        """
        Take range of two dates and return all affected dates
        """
        date_from = datetime.strptime(date_from, DTF)
        date_to = datetime.strptime(date_to, DTF)
        for n in range(int((date_to - date_from).days) + 1):
            yield date_from + timedelta(n)

    def compute_days(self, number_of_days, date_from, date_to):
        """
        From a range of dates, compute the number of days that should be
        deducted from the leave (not counting weekends and public holidays)
        """
        if self.employee_id:
            self.number_of_days_temp = self.deduct_special_days(number_of_days)
        else:
            self.number_of_days_temp = number_of_days


    def deduct_special_days(self, number_of_days=0):
        """
        Remove the number of special days from the days count
        """
        days_to_deduct = 0
        special_days = self.get_special_days(self.date_from, self.date_to,
                                             self.employee_id)
        
        for date in special_days:
            days_to_deduct += 1

        days_without_special_days = number_of_days - days_to_deduct
        self.test=days_without_special_days
        return days_without_special_days

    def get_special_days(self, date_from, date_to, employee):   
        """
        Return dict of special days (Date: Name)

        Partly Deprecated: Since we now generate actual leave entries for
        public holidays they do no longer need to be deducted from the number
        of days (overlapping leaves cannot be created anyway). We should
        keep removing Sat/Sun and probably make it possible to remove other
        weekdays as well for countries with other work schedules
        """
        public_leave_ids = self.env['hr.holidays.public.line'].search([
            ('state_ids', 'in', employee.company_id.state_id.id)]
        )
        #deduct_saturday = employee.company_id.deduct_saturday_in_leave
        #deduct_sunday = employee.company_id.deduct_sunday_in_leave
        special_days = {}
        for date in self.daterange(date_from, date_to):
            date_str = str(date.date())
            public_leave = public_leave_ids.filtered(
                lambda r: r.date == date_str)
            weeks = {'monday': 'Monday' ,'tuesday' : 'Tuesday', 'wednesday': 'Wednesday', 'thursday' : 'Thursday', 'friday' : 'Friday', 'saturday' : 'Saturday','sunday' : 'Sunday'}
            second_week_off=employee.address_id.second_week_off
            first_week_off=employee.address_id.first_week_off
            if public_leave:
                special_days[date.date()] = 'Public Holiday: %s' \
                                            % public_leave.name
            elif first_week_off and date.strftime("%A") == weeks[first_week_off] :
                special_days[date.date()] = 'first_week_off'
            elif second_week_off and date.strftime("%A") == weeks[second_week_off]:
                special_days[date.date()] = 'second_week_off'
        return special_days
            
        
        
