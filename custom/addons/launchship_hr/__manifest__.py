# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2018 - Today Kiran Marati.
#
#    @author Marati Kiran (kiran.marati@gmail.com)
#
##############################################################################

{
    'name': 'Launchship HR',
    'version': '1.0',
    'sequence': 125,
    'category': 'Human Resources',
    'description': """
        Customizations on HR module.
        Employee will get email notification when his/her leave approved or rejected
        Customized for Launchship Technology Solutions Pvt.Ltd.
        """,
    'author': "Launchship Technologies",
    'website': "http://www.launchship.com",

    'depends': ['base','hr', 'hr_holidays','mail','web'],
    'summary': 'Employee view modifications',
    'data': [
        'data/leave_email_templates.xml',
        'data/wish_cronjob.xml',
        'data/wishesh_email_templates.xml',
        'data/hr_holiday_data.xml',
        'views/hr_form_view.xml',
        'views/hr_holidays_view.xml',
        'security/ir.model.access.csv',
        'security/hr_security.xml',
        'security/hr_holidays_security.xml',
        # 'security/hr_attendance_security.xml',

     
        'views/hide_leave_summary_print_in_actions.xml',
        # 'views/hr_attendance_view.xml',
        #'views/leave_approval_mail_view.xml',
        # 'views/hide_manage_db_link.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True
}
