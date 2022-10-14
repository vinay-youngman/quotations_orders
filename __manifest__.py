# -*- coding: utf-8 -*-
{
    'name': "quotations_orders",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ajay",
    'website': "https://www.youngman.co.in/",

    
    'category': 'Uncategorized',
    'version': '2.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'jobsites'],

    # always loaded
    'data': [
        'views/sale_order_form.xml',
        'report/sale_report_inherit.xml',
    ],
}
