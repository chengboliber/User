# _*_ coding: utf_8 _*_


import os
import sys

_basedir = os.path.abspath(os.path.dirname(__file__))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)


from flask.ext.script import Manager
from user.users import models as users_models
from user import api

manager = Manager(api.create_app())


@manager.command
def create_db():
    """create video database table structure
    """
    users_models.create_all()


@manager.command
def drop_db():
    """drop video database table structure
    """
    users_models.drop_all()


if __name__ == '__main__':
    manager.run()
