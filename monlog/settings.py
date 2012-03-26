# Monlog settings
# Please enter your database info here:
DATABASE_NAME     = ""
DATABASE_USER     = ""
DATABASE_PASSWORD = ""
DATABASE_HOST     = ""
DATABASE_PORT     = ""
DATABASE_DRIVER   = "mysql"

import os
import django

# Constant to use for relative paths in settings
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

API_LIMIT_PER_PAGE = 0

FIXTURE_DIRS = ('./log/fixtures',)
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'log/templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'mpici!$-&5b9(woqx9!wm1y*#96jpo-drz-nqghhj*gk90@h4i'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'monlog.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tastypie',
    'django.contrib.admin',
    'monlog.log',
    'django_extensions',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOG_DIR = os.path.join(SITE_ROOT, '../logging/')
LOGGING = {
   'version': 1,
   'disable_existing_loggers': True,
   'formatters': {
       'verbose': {
           'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
       },
       'simple': {
           'format': '%(levelname)s %(message)s'
       }
   },
   'handlers': {
       'file_info' : {
           'level': 'INFO',
           'class': 'logging.FileHandler',
           'filename': '%s/django_info.log' % LOG_DIR,
           'formatter': 'verbose'
       },
       'file_debug': {
           'level': 'DEBUG',
           'class': 'logging.FileHandler',
           'filename': '%s/django_debug.log' % LOG_DIR,
           'formatter': 'verbose'
       },
       'file_error': {
           'level': 'ERROR',
           'class': 'logging.FileHandler',
           'filename': '%s/django_error.log' % LOG_DIR,
           'formatter': 'verbose'
       },
       'mail_admins': {
           'level': 'ERROR',
           'class': 'django.utils.log.AdminEmailHandler'
       }
   },
   'loggers': {
       '' : {
           'handlers': ['file_info'],
           'level': 'INFO',
           'propagate': True,
       },

       'django': {
           'handlers': ['file_info'],
           'level': 'INFO',
           'propagate': True,
       },
       'django.request': {
           'handlers': ['file_error'],
           'level': 'ERROR',
           'propagate': True,
       },
   }
}

# local_settings.py is in .gitignore, put your database settings there
try:
    from local_settings import *
except ImportError:
    DATABASES = {
        'default': {
            'ENGINE': "django.db.backends.%s" % DATABASE_DRIVER,
            'NAME': DATABASE_NAME,
            'USER': DATABASE_USER,
            'PASSWORD': DATABASE_PASSWORD,
            'HOST': DATABASE_HOST,
            'PORT': DATABASE_PORT,
        }
    }
