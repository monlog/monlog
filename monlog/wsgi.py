# This assumes that your virtual environment is located at:
# /path/to/monlog/venv
import os, sys, site

# parent directory of wsgi.py
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project = os.path.dirname(os.path.abspath(__file__))

# add the virtual environment
site.addsitedir(os.path.join(parent, 'venv', 'lib', "python%s.%s" % (sys.version_info[0], sys.version_info[1]), 'site-packages'))

sys.path.append(parent)
sys.path.append(project)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monlog.settings")

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
