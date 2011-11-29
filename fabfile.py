from fabric.api import env, local, run, sudo, settings as fabric_settings
from fabric.context_managers import cd, show
from fabric.contrib.files import append, exists, put, sed
from fabric.operations import require, prompt, get, put
from fabric.state import output
from fabric.utils import abort

def test():
    local('py.test test_tracerbull.py')
