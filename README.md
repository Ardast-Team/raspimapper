This is a django mapper using the default Django recommendations
IMPORTANT: This version is Functioning! 10/09/2024


python3 -m venv venv
source venv/bin/activate

pip install pip --upgrade
or
python.exe -m pip install --user --upgrade pip

pip install django

cd ..
django-admin startproject mapper
cd mapper

# TO START:
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver




# OLD:

# DJSUPERVISOR
pip install supervisor
pip install watchdog
copy djsupervisor folder
copy supervisor.conf
include djsupervisor in settings.py INSTALLED_APPS

# BOTS
pip install django-q
pip install django-debug-toolbar
copy bots
copy bots.ini
in urls.py-> import debug_toolbar
in urls.py-> path('__debug__/', include(debug_toolbar.urls)),
in urls.py-> path('bots/', include('bots.urls')),
in settings.py-> 'bots', 'django_q' and 'debug_toolbar' in INSTALLED_APPS
in manage.py -> add bots requireents

in settings.py:
add CUSTOM SETTING
python manage.py createcachetable -> required for CACHE setting

python manage.py makemigrations
python manage.py migrate

# import PLUGIN
Import

change:
bots.botsconfig -> bots.utils.botsconfig
bots.botslib -> bots.utils.botslib 