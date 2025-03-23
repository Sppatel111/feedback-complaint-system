from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from admin.admin import admin
from user.user import user
from flask_login import LoginManager
from models import db,User
app=Flask(__name__)

app.config['SECRET_KEY'] = '9c6a7d0a3e4f2b1c8d5e9f7a2b3c4d6e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sneha@localhost:5432/management'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate()
db.init_app(app)

app.register_blueprint(admin,url_prefix='/admin')
app.register_blueprint(user,url_prefix='/user')
migrate.init_app(app,db)

user_login_manager=LoginManager()
user_login_manager.init_app(app)
user_login_manager.login_view = "user.login"

admin_login_manager=LoginManager()
admin_login_manager.init_app(app)
admin_login_manager.login_view = "admin.login"

# @user_login_manager.user_loader
# def load_user(user_id):
#     return db.get_or_404(User,email=user_id,role='employee')
#
# @admin_login_manager.user_loader
# def load_admin(user_id):
#     return db.get_or_404(User,email=user_id,role='admin')

@user_login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(email=user_id, role='employee').first()

@admin_login_manager.user_loader
def load_admin(user_id):
    return User.query.filter_by(email=user_id, role='admin').first()



@app.route('/')
def user_login():
    return redirect(url_for('user.login'))

if __name__ =='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)