# -*- coding: utf-8 -*-
{
    'name': "Biometric Attendance",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Launchship Technologies",
    'website': "http://www.launchship.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/biometric_attendance.xml',
        'data/biometric_attendance_email_template.xml',
        'security/hr_biometric.xml',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    'images': ['static/description/hr_biometric_device.png'],
    # only loaded in demonstration mode
    
    'installable': True,
    'application': True,
}
