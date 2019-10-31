# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2009-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Niyas Raphy(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, tools, _

class LeaveApproval(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def action_confirm(self):
        res = super(LeaveApproval, self).action_confirm()
        logging.info('confirmmmmmmmmmmmmmmm')
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('launchship_hr', 'email_template_leave_request')[1]
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=False)
        return res
    
    @api.multi    
    def action_validate(self):
        res = super(LeaveApproval, self).action_validate()
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('hr_holidays', 'email_template_leave')[1]
        manager = self.manager_id
        employee_mail = self.employee_id.work_email
        employees = self.env['hr.employee'].search(['|',('parent_id', '=', manager.id),('parent_id','=',self.employee_id.id )])
        ids = []
        if employees:
          for emp in employees:
            ids.append(emp.work_email)
          if employee_mail in ids:
            ids.remove(employee_mail)
          email_ids = ','.join(ids) 
          x = self.env['mail.template'].browse(template_id)
          x.write({'email_cc': email_ids})
          x.send_mail(self.id, force_send=True)

        template_id = ir_model_data.get_object_reference('launchship_hr', 'email_template_leave')[1]
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=False)
        return res
    
    @api.multi
    def action_refuse(self):
        res = super(LeaveApproval, self).action_refuse()
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('launchship_hr', 'email_template_leave_rejection')[1]
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=False)
        return res
