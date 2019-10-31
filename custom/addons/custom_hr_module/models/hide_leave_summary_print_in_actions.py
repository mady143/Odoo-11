#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, date
import calendar
import logging



class Print(models.TransientModel):
   _inherit = 'hr.holidays.summary.employee'
   _description = 'HR Leaves Summary Report By Employee'

   hide = fields.Boolean(string='Hide', default=True)

   @api.multi
   @api.onchange('date_from')
   def _compute_hide(self):
      employee = self.env.context.get('active_ids', []) 
      employees = self.env['hr.employee'].browse(employee)
     #  show the print button for CEO group 
      if self.env.user.has_group('launchship_hr.group_hr_holidays_ceo1') or employees.user_id.id == self.env.uid or employees.parent_id.user_id.id==self.env.uid or employees.parent_id.parent_id.user_id.id==self.env.uid: 
       self.hide = True
      else:
       self.hide=False


            
            
