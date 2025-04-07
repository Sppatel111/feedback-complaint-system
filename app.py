from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from admin.admin import admin
from user.user import user,UPLOAD_FOLDER
from flask_login import LoginManager,current_user
from models import db, User
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = '9c6a7d0a3e4f2b1c8d5e9f7a2b3c4d6e'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('database')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# print("Database URL:",app.config['SQLALCHEMY_DATABASE_URI'])

db.init_app(app)
migrate = Migrate()

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(user, url_prefix='/user')
migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# @app.before_request
# def before_request():
#     print(f"Current user: {current_user}")
#     print(f"Is authenticated: {current_user.is_authenticated}")
#     print(f"User role: {getattr(current_user, 'role', 'No role')}")


@app.route('/')
def user_login():
    return redirect(url_for('user.login'))


with app.app_context():
    db.create_all()

if __name__ == '__main__':

    app.run(debug=True)


