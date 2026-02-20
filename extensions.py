from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
login = LoginManager()
csrf = CSRFProtect()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address)