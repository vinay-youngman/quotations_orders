# -*- coding: utf-8 -*-

{
    'name': "Quotations & Orders",
    'version': '2.3',
    'category': 'Sales/CRM',
    'summary': 'It provides modification in SalesOrder Module.',
    'description': """
        Provides Quotations & Orders Modifications
    """,
    'author': "Ajay",
    'website': "https://www.youngman.co.in/",
    'sequence': -100,

    'depends': ['sale_management', 'sale', 'jobsites', 'youngman_customers'],

    'data': [
        'views/sale_order_form.xml',
        'report/sale_report_inherit.xml',
        'security/ir.model.access.csv',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
