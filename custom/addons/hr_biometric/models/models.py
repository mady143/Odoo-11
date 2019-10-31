#  -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta
from datetime import datetime
import datetime
from decimal import Decimal
import sys
import pytz
import calendar
sys.path.append("zk")
from zk import ZK, const
import csv
import datetime
class hr_biometric(models.Model):

  _name = 'hr_biometric.hr_biometric'
  device_ip = fields.Char(string="Device IP")
  device_port = fields.Integer(string="Device Port")
  checkin_status      = fields.Char(string="Checkin Status")
  checkout_status      = fields.Char(string="Checkout Status")

  def download_cron_attendance(self):
    attendance_data =  self.env['hr_biometric.hr_biometric'].search([])
    for data in attendance_data:
      data.download_attendance()

  def download_attendance(self):
    
    machine_ip = self.device_ip
    port_no    = self.device_port
    status_checkin = self.checkin_status
    status_checkout = self.checkout_status

    stat1 = status_checkin.split(",")
    stat1 = [int(i) for i in stat1]
    stat2 = status_checkout.split(",")
    stat2 = [int(i) for i in stat2]
    zk1 = ZK(machine_ip, port_no)
    conn = zk1.connect()
    users_data = []
    if conn:
      
      record_count_attendance_log = self.env['attendance_log'].search_count([])
      record_count_checkin_checkout_log = self.env['checkin_ckeckout_log'].search_count([])
      tempattendance = []

      attendance = conn.get_attendance()
      date_time_formate = '%Y-%m-%d %H:%M:%S'
      if record_count_attendance_log != 0:
        latest_datetime = datetime.datetime.strptime(self.env['attendance_log'].search([], limit=1, order='id desc').timestamp,date_time_formate)
        for att in attendance:
          if datetime.datetime.strptime(str(att.timestamp-timedelta(hours=5,minutes=30)),date_time_formate)  > latest_datetime:
            tempattendance.append(att)
        attendance = tempattendance

      for att in attendance:
        UserId = att.user_id
        time   = att.timestamp
        Timestamp = time-timedelta(hours=5, minutes=30)
        date= Timestamp.date()
        status  = att.status

        if status in stat1:
          status_check = "Checkin"
          CheckIn = Timestamp
          CheckOut = ''
            
        if status in stat2:
          status_check = "Checkout"
          CheckIn = ''
          CheckOut = Timestamp

        
        employee_details = self.env["hr.employee"].search([('emp_number','=',UserId)])
        employee_id = employee_details.id
        resource_id = employee_details.resource_id
        users_id        = resource_id.user_id.id
        name = employee_details.name
        email = employee_details.work_email
        if att.status in stat1:
          att_log_checkin = self.env['attendance_log'].search([('checkout','=',False),('user_id','=',UserId),('date','=',date)])
          if (att_log_checkin):
            self.env.cr.execute("update attendance_log set checkin=%s where user_id=%s and checkout=%s", (CheckIn,UserId,None))
          else:
            create_att_log = self.env['attendance_log'].create({'user_id':UserId,'users_id':users_id,'user_name':name,'user_email':email,'date':date,'timestamp':Timestamp,'checkin':CheckIn})
        if att.status in stat2:
          att_log_checkout =self.env['attendance_log'].search([('checkout','=',False),('user_id','=',UserId),('date','=',date)])
          if att_log_checkout:
            check_in = datetime.datetime.strptime(att_log_checkout.checkin,date_time_formate)
            worked_hours = CheckOut - check_in
            total_worked_hours = worked_hours.total_seconds() / 3600
            att_log_checkout.write({'checkout':CheckOut,'worked_hours':total_worked_hours})



      self.env.cr.execute("select user_id,user_name,user_email,users_id,sum(worked_hours),date(timestamp) as Date,min(checkin) as checkin,max(checkout) as checkout,CASE WHEN MAX(checkout) is null THEN 0 ELSE EXTRACT(EPOCH FROM (MAX(checkout)-MIN(checkin)))/3600 END AS HoursWorked from attendance_log group by user_id,user_name,user_email,users_id,date(timestamp) order by Date")
      for data in self._cr.dictfetchall(): 
        user_id = data['user_id']
        name=data['user_name']
        email=data['user_email']
        users_id=data['users_id']
        worked_hours = data['sum']
        date    = data['date']
        user_checkin_checkin = data['checkin']
        user_checkout_checkout = data['checkout']
        working_hours    = data['hoursworked']
        break_hours      = working_hours - worked_hours
        if record_count_checkin_checkout_log == 0:
          self.env['checkin_ckeckout_log'].create({'user_id':user_id,'user_name':name,'user_email':email,'users_id':users_id,'date':date,'user_checkin':user_checkin_checkin,'user_checkout':user_checkout_checkout,'working_hours':working_hours,'worked_hours':worked_hours,'break_hours':break_hours})
        else:
          mincheckin_maxcheckin_log = self.env['checkin_ckeckout_log'].search([('user_id','=',user_id),('date','=',date)])
          if mincheckin_maxcheckin_log:
            mincheckin_maxcheckin_log.write({'user_checkout':user_checkout_checkout,'working_hours':working_hours,'worked_hours':worked_hours,'break_hours':break_hours})
          else:
            self.env['checkin_ckeckout_log'].create({'user_id':user_id,'user_name':name,'user_email':email,'users_id':users_id,'date':date,'user_checkin':user_checkin_checkin,'user_checkout':user_checkout_checkout,'working_hours':working_hours,'worked_hours':worked_hours,'break_hours':break_hours})



class hr_biometric_attendance_log(models.Model):
  _name = 'attendance_log' 
  _order = 'date desc,user_name asc'

  user_id = fields.Char(string="User Id",size=10)
  users_id = fields.Integer(string="Users Id")
  user_name = fields.Char(string = "Name")
  user_email = fields.Char(string = "Email")
  date    = fields.Date(string="Date")
  timestamp = fields.Datetime(string="Timestamp")
  status   = fields.Char(string="Type")
  checkin = fields.Datetime(string="CheckIn")
  checkout = fields.Datetime(string="Checkout")
  worked_hours  = fields.Float(string="Total Worked Hours",size=2,default=0)

class hr_biometric_attendance_checkin_ckeckout_log(models.Model):
  _name = 'checkin_ckeckout_log'
  _order = 'date desc,user_name asc'


  user_id = fields.Char(string="User Id")
  user_name    = fields.Char(string="Name")
  user_email   = fields.Char(string="Email")
  date  = fields.Datetime(string="Date")
  user_checkin = fields.Datetime(string="CheckIn",default=0)
  user_checkout = fields.Datetime(string="Checkout",default=0)
  users_id          =fields.Integer(string="U ID")
  working_hours  = fields.Float(string="Total Hours",size=2,default=0)
  worked_hours   = fields.Float(string="Worked Hours", size=2,default=0)
  break_hours    = fields.Float(string="Break Hours",size=2,default=0)
  
  def att_log_func(self):
    att_log = self.env['attendance_log'].search([('user_id','=',self.user_id),('date','=',self.date)]).ids
    view_id_tree = self.env['ir.ui.view'].search(
             [('name','=',"hr_biometric_attendance_log")])
    domain = [('id', 'in',  att_log)]
    return {
         'type': 'ir.actions.act_window',
         'name':self.user_name,
         'res_model': 'attendance_log',
         'view_type': 'form',
         'view_mode': 'tree,form',
         'views': [(view_id_tree[0].id, 'tree'),(False,'form')],
         'domain': domain,
        }

  def send_biometric_attendance_no_checkout_email(self):
    date_time_formate = '%Y-%m-%d %H:%M:%S'
    date_fromate      = '%Y-%m-%d 00:00:00'
    ir_data = self.env['ir.model.data']
    wish_template = ir_data.get_object('hr_biometric', 'biometric_attendance_email_template')
    date_today = datetime.datetime.today()
    yesterday_date = date_today-timedelta(days=1)
    yesterday = datetime.datetime.strftime(yesterday_date,date_fromate)
    yesterday_date_weekday = yesterday_date.weekday()
    today_weekday = datetime.datetime.today().weekday() 
    week_day = list(calendar.day_name)
    weekdays_list = self.env['weekdays_list'].search([])
    week_off_list=weekdays_list.week_offs.split(',')
    week_days_list=weekdays_list.working_days.split(',')
    
    checkin_checkout_log = self.env['checkin_ckeckout_log'].search([('user_checkout','=',False),('date','=',yesterday)]).ids
    checkin_checkout_log_ids = self.env['checkin_ckeckout_log'].search([('id','in',checkin_checkout_log)])
    for user_id in checkin_checkout_log_ids:
      
      users_id = user_id.user_id
      ids = user_id.user_email
      today_date = user_id.date
      today = datetime.datetime.strptime(today_date, date_time_formate).weekday()

      self.env.cr.execute("select date from hr_holidays_public_line")
      for public_holidays_list in self._cr.dictfetchall():
        public_holidays_list_date = public_holidays_list['date']

      if not week_day[today] in week_off_list and today != today_weekday  and today != public_holidays_list_date:
        
        wish_template.sudo().send_mail(user_id.id, force_send=False)
      

  def send_biometric_attendance_no_checkin_email(self):
    date_time_formate = '%Y-%m-%d %H:%M:%S'
    date_fromate       = '%Y-%m-%d 00:00:00'
    ir_data = self.env['ir.model.data']
    wish_template = ir_data.get_object('hr_biometric', 'biometric_attendance_no_checkin_email_template')
    today = datetime.datetime.today().strftime(date_fromate)
    today_date = datetime.datetime.now().strftime(date_time_formate)
    date_today = datetime.datetime.today()
    yesterday_date = date_today-timedelta(days=1)
    yesterday = datetime.datetime.strftime(yesterday_date,date_fromate)
    yesterday_date_weekday = yesterday_date.weekday()

    week_day = list(calendar.day_name)
    print("week_day[yesterday_date_weekday]:",week_day[yesterday_date_weekday])
    weekdays_list = self.env['weekdays_list'].search([])
    week_off_list=weekdays_list.week_offs.split(',')
    week_days_list=weekdays_list.working_days.split(',')
    self.env.cr.execute("select date from hr_holidays_public_line")
    for public_holidays_list in self._cr.dictfetchall():
      public_holidays_list_date = public_holidays_list['date']

    checkin_checkout_log = self.env['checkin_ckeckout_log'].search([('date','=',yesterday)]).ids
    checkin_checkout_log_ids = self.env['checkin_ckeckout_log'].search([('id','in',checkin_checkout_log)])
    employee_record = self.env['hr.employee'].search([])
    employee_record_log = self.env['hr.holidays'].search([('type','=','remove'),('date_from','<',yesterday)]).ids
    employee_record_log_ids = self.env['hr.holidays'].search([('id','in',employee_record_log)])
    holidays_ids=[]
    employee_ids=[]
    user_ids=[]
    for emp_id in employee_record:
      employee_ids.append(emp_id.id)
    for holidays in employee_record_log_ids:
      holidays_ids.append(holidays.employee_id.id)
    holidays_log_ids = [i for i in employee_ids if i not in holidays_ids]
    employee_log_ids = self.env['hr.employee'].search([('id','in',holidays_log_ids)])

    employee_num=[]
    for ids in employee_log_ids:
      employee_num.append(ids.emp_number)
    for user_id in checkin_checkout_log_ids:
      user_ids.append(user_id.user_id)

    user_ids_list = [j for j in employee_num if j not in user_ids]

    email_ids = self.env['hr.employee'].search([('emp_number','in',user_ids_list)])
    emailids=[]

    for users in email_ids:
      emailids.append(users.work_email)
      if not week_day[yesterday_date_weekday] in week_off_list and yesterday_date_weekday != today_weekday  and yesterday_date_weekday != public_holidays_list_date:
        wish_template.sudo().send_mail(users.id, force_send=False)
        


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    def login_user_att(self):
      checkin_ckeckout_log = self.env['checkin_ckeckout_log'].search([('user_id','=',self.emp_number)]).ids
      view_id_tree = self.env['ir.ui.view'].search(
               [('name','=',"hr_biometric_attendance_checkin_checkout")])
      domain = [('id', '=', checkin_ckeckout_log)]
      return {
           'type': 'ir.actions.act_window',
           'name': 'Attendance Log',
           'res_model': 'checkin_ckeckout_log',
           'view_type': 'form',
           'view_mode': 'tree,form',
           'views': [(view_id_tree[0].id, 'tree'),(False,'form')],
           'domain': domain,
          }





class Weekdays_list(models.Model):
  _name = 'weekdays_list'
  _rec_name= "working_days"
  working_days   = fields.Char(string='Working Days')
  week_start_day      = fields.Char(string='Week Start Day')
  week_end_day       = fields.Char(string='Week End Day')
  week_offs       = fields.Char(string='WeekOffs')


class Weekdays(models.Model):
  _name = 'days'
  _rec_name= "working_days"
  working_days = fields.Char(string='Working Days')
