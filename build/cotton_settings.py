# cotton_settings.py
#   -- Tell cotton how to deploy your application
#
# Import the default settings directly into the current namespace, so that you can combine,
# extend, and override the defaults with settings unique to your application deployment.
from cotton.settings import *
import os

# Name your project here. Will be used as a directory name, so be sensible.
PROJECT_NAME = 'hello'

# deploy the appplication to /usr/local/deploy/sprobot/, creating
# bin/, lib/, project/ and so on at that location.
VIRTUALENV_PATH = os.path.join(VIRTUALENV_HOME, PROJECT_NAME)

# Where the application code (ie, the contents of the current directory) will be deployed.
PROJECT_ROOT = os.path.join(VIRTUALENV_PATH, 'project')

# A list of target nodes which cotton should (optionally) bootstrap and deploy your app to
HOSTS = ['108.61.229.81', '104.207.143.24']

# A list of IPv4 addresses that should be granted administrative access. This includes
# permitting SSH access, and may be leveraged for additional purposes in your ap
ADMIN_IPS = ['74.111.177.5']

# The system user and group that should execute your application. The user will be created
# by cotton automatically, if it doesn't already exist. Existing users should not have extra
# privileges, including sudo access.
PROJECT_USER = 'hello'
PROJECT_GROUP = 'hello'

PIP_REQUIREMENTS_PATH += [COTTON_PATH + '/../requirements/pip.txt']
APT_REQUIREMENTS_PATH += [COTTON_PATH + '/../requirements/apt.txt']

# If True, do not prompt for confirmation of dangerous actions. Required for unattended operation,
# but dangerous in mixed (ie, dev/testing) environments, so disabled by default.
#
# NO_PROMPTS = False

# The timezone the HOSTS should be in. Cotton defaults to UTC; you can override that here.
TIMEZONE = "America/New_York"

# By default cotton assumes your application is in a git repository, and that git can be used
# to deploy the application source to the HOSTS.
#
#USE_GIT = True

# If you want your HOSTS to run an SMTP server for outbound mail, set SMTP_HOST=True. You can
# specify a relay host with SMTP_RELAY.
SMTP_HOST = True
#SMTP_RELAY = None

FIREWALL += [
    "allow proto tcp from any to %(public_ip)s port 80",

    # in the real world we wouldn't do this; cotton's system module would
    # add a rule permitting inbound SSH for ADMIN_IPS, defined above. This
    # exception is for the slack test.
    "allow proto tcp from any to %(public_ip)s port 22",
]

# absurdly low values here, since hello-world doesn't need it.
APACHE_LIMITREQUESTBODY = 4096
APACHE_TIMEOUT = 10

APACHE_MAXKEEPALIVEREQUESTS = 256
APACHE_KEEPALIVETIMEOUT = 3

TEMPLATES += [
    {
        "name": "apache2",
        "local_path": COTTON_PATH + "/../templates/apache2.conf",
        "remote_path": "/etc/apache2/apache2.conf",
        "reload_command": "/etc/init.d/apache2 restart"
    },
    {
        "name": "apache2_security",
        "local_path": COTTON_PATH + "/../templates/apache2_security",
        "remote_path": "/etc/apache2/conf.d/security",
        "reload_command": "/etc/init.d/apache2 reload"
    },
    {
        "name": "apache2_vhost",
        "local_path": COTTON_PATH + "/../templates/apache2_vhost.conf",
        "remote_path": "/etc/apache2/sites-available/hello",
        "reload_command": "cd /etc/apache2 && "
                          "rm -f sites-enabled/000-default && "
                          "ln -s /etc/apache2/sites-available/hello"
                          " sites-enabled/000-default && "
                          "/etc/init.d/apache2 reload"
    },
    {
        "name": "php.ini",
        "local_path": COTTON_PATH + "/../templates/php.ini",
        "remote_path": "/etc/php5/apache2/php.ini",
        "reload_command": "/etc/init.d/apache2 reload"
    },
    {
        "name": "sshd_config",
        "local_path": COTTON_PATH + "/../templates/sshd_config",
        "remote_path": "/etc/ssh/sshd_config",
        "reload_command": "/etc/init.d/ssh reload",
    },
    {
        "name": "sysctl_params",
        "local_path": COTTON_PATH + "/../templates/sysctl_params.conf",
        "remote_path": "/etc/sysctl.d/30-hello.conf",
        "reload_command": "/etc/init.d/procps restart",
    },
    {
        "name": "unattended_upgrades",
        "local_path": COTTON_PATH + "/../templates/50unattended-upgrades",
        "remote_path": "/etc/apt/apt.conf.d/50unattended-upgrades",
        "reload_command": "/etc/init.d/unattended-upgrades restart"
    },
]


ENSURE_RUNNING += ['apache2', 'postfix']
