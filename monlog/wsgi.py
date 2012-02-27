import os, sys, site

# parent directory of wsgi.py
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# add the virtual environment
site.addsitedir(os.path.join(path, 'venv', 'lib', "python%s.%s" % (sys.version_info[0], sys.version_info[1]), 'site-packages'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monlog.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
