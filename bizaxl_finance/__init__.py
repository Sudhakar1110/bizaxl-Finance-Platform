# -*- coding: utf-8 -*-
from frappe import _

__version__ = "1.0.0"


def get_context(context):
    context.update({
        "app_name": "Bizaxl Finance",
        "app_version": __version__,
        "app_title": "Bizaxl Finance",
        "app_description": "Complete Financial Services Platform",
        "app_publisher": "Bizaxl Technologies",
        "app_email": "info@bizaxl.com",
        "app_url": "https://bizaxl.com",
        "app_icon": "octicon octicon-credit-card",
        "app_color": "blue",
        "app_logo_url": "/assets/bizaxl_finance/images/logo.png",
    })
