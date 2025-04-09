import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '00000'
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://postgressm_6wxf_user:vosOmiYRzX5blM6wrbtvwyNAixCrXVkC@dpg-cvqs18a4d50c73es99gg-a/postgressm_6wxf') or \
        'postgresql://postgressm_6wxf_user:vosOmiYRzX5blM6wrbtvwyNAixCrXVkC@dpg-cvqs18a4d50c73es99gg-a/postgressm_6wxf' + os.path.join(basedir, 'instance', 'business.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
