"""
Django settings for games_list project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gamestest',
        'HOST': 'games-list.cxotlb2v8xd7.us-west-2.rds.amazonaws.com',
        'PORT':'3306',
        'USER':'jubio',
        'PASSWORD':'Mithras25'
    }
}

