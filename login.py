from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from main import app