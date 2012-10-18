# coding=UTF-8
# Our own settings for trybar

UPLOAD_ROOT = 'd:/projects/trybar/uploads/'     # needs to have trailing slash
UPLOAD_PATH = '/uploads/'   # needs to have trailing slash

MAIL_FROM = 'kontakt@trybar.pl'
MAIL_FRIENDLY_FROM = 'Trybar'
MAIL_USER = 'kontakt@trybar.pl'
MAIL_PASS = 'maslana'
MAIL_SERVER = 'mail.trybar.linuxpl.info'
MAIL_PORT = 587

# Django settings for trybar project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'trybar',             
#        'USER': 'postgres',                   
#        'PASSWORD': 'bohrok2405',             
#        'HOST': '',                
#        'PORT': '',                
#    }
#}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',             
        'USER': '',                   
        'PASSWORD': '',             
        'HOST': '',                
        'PORT': '',                
    }
}


TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'pl'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = 'd:/projects/trybar/media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'z-n4r*ee+x#xc(7y)0qi9vzmw4f&#pyf(f-lq)!8@$x549fer9'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #    'django.contrib.messages.middleware.MessageMiddleware',
    'trybar.account.middleware.AuthenticationManagementMiddleware',
)

ROOT_URLCONF = 'trybar.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    'D:/projects/trybar/templates/',
)

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.humanize',
    'trybar.account',
    'trybar.bar',
    'trybar.adverts',
    'trybar.barevent',
    'trybar.main',
    'trybar.core',
    'trybar.photo',
    'trybar.barevent',
    'trybar.search',
    'trybar.ranking',
    'trybar.scoring',
    'trybar.accnews',
#    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}