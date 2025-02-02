from flask_assets import Environment
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

assets = Environment()
auth = HTTPBasicAuth()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.session_protection = "strong"
