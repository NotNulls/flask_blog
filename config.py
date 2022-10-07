import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "'9a40917e4c539ade06ee9b2e63754df14620b8be199bfa5f5c00da80219adfee'"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///'+ os.path.join(base_dir,'app.db')
    # line below is the feature sending signals to the application every time a change is about to be mades
    SQLALCHEMY_TRACK_MODIFICATIONS = False
