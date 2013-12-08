"""
Django settings for lolTrueStory project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qe0q9glt7x3=s-uqrpztfcad%!df)uzw1_4s7f$lcekovw&-d5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',
    'polls',
    'mainsite',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.FailedLoginMiddleware',
)

ROOT_URLCONF = 'lolTrueStory.urls'

WSGI_APPLICATION = 'lolTrueStory.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}"""

try:
    from dbsettings import *
except ImportError:
    pass

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Denver'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# The number of login attempts allowed before a record is
#created for the failed logins.
#Default= 3
AXES_LOGIN_FAILURE_LIMIT=3

# After the number of allowed login attempts are exceeded,
#should we lock out this IP (and optional user agent)?
#Default: True
AXES_LOCK_OUT_AT_FAILURE=5

# If True, lock out / log based on an IP address AND a
#user agent. This means requests from different user
#agents but from the same IP are treated differently.
#Default: False                           
AXES_USE_USER_AGENT=False

# If set, defines a period of inactivity after which
#old failed login attempts will be forgotten. Can be
#set to a python timedelta object or an integer. If an
#integer, will be interpreted as a number of hours.
#Default: None
AXES_COOLOFF_TIME=1

# If set, specifies a logging mechanism for axes to use.
#Default: 'axes.watch_login'
#AXES_LOGGER=

# If set, specifies a template to render when a user is
#locked out. Template receives cooloff_time and
#failure_limit as context variables.
#Default: None
AXES_LOCKOUT_TEMPLATE="mainsite/login.html"

# If set, specifies a URL to redirect to on lockout. If
#both AXES_LOCKOUT_TEMPLATE and AXES_LOCKOUT_URL are set,
#the template will be used.
#Default: None
#AXES_LOCKOUT_URL=

# If True, you'll see slightly more logging for Axes.
#Default: True
AXES_VERBOSE=True
