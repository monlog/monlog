Introduction
------------
Monlog is a Django project. Django is a web framework built in Python and as such will run anywhere Python does.

Monlog uses a relational database and is built with MySQL as the primary database target, which was a project requirement.

How to install
--------------
These are short instructions on how to install Monlog on an Apache/MySQL stack on a Debian/Ubuntu system.

Requirements:
* Python 2.5 or better
* Git (since these instructions assume you'll want to update frequently since Monlog is still very much under development)

We'll be using the mod_wsgi Apache module, so install it now:

    apt-get install libapache2-mod-wsgi

To be able to compile and use Python's MySQL driver, install these dependencies:

    apt-get install libmysqlclient-dev python-dev

Also install Python's virtualenv and pip, for Python dependency resolution:

    apt-get install python-virtualenv python-pip

Decide where you want to place Monlog. It needs to be accessible by the user running Apache, but not inside your www directory. For this guide we'll assume you're placing Monlog in your home directory.

Clone Monlog into your home directory:

    git clone https://github.com/monlog/monlog
    
Add submodules to the repo:

    git submodule init
    git submodule update

Allow Apache access to the monlog directory (this assumes you are in the www-data group):

    chgrp -R www-data ~/monlog

Create a so-called virtualenv for Monlog to run in, to stop it from interfering with your system Python:

    virtualenv --no-site-packages ~/monlog/venv

Enter the virtual environment and install Monlog's Python dependencies:

    . ~/monlog/venv/bin/activate
    pip install -r ~/monlog/requirements.txt

Open ~/monlog/monlog/settings.py and add your database information at the top of the file

(Re-)enter the virtual environment and create a logging directory in ~/monlog/logging
then have Monlog create its database tables:

    . ~/monlog/venv/bin/activate
    mkdir ~/monlog/logging/
    python ~/monlog/monlog/manage.py syncdb

You'll be asked to create a superuser account, make sure you remember it!

Add an Apache site for Monlog by putting the below in /etc/apache2/sites-available/monlog

    <VirtualHost *:80>
            ServerName monlog

            Alias /static/ /path/to/monlog/monlog/static/

            <Directory /path/to/monlog/monlog/static>
                    Order deny,allow
                    Allow from all
            </Directory>

            WSGIScriptAlias / /path/to/monlog/monlog/wsgi.py

            <Directory /path/to/monlog/monlog>
                    <Files wsgi.py>
                            Order allow,deny
                            Allow from all
                    </Files>
            </Directory>

            LogLevel warn
            ErrorLog /var/log/apache2/monlog_error.log
            CustomLog /var/log/apache2/monlog_access.log combined
    </VirtualHost>

Enable the Apache site and reload:

    a2ensite monlog
    service apache2 reload
