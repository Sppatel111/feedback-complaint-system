from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from admin.admin import admin
from user.user import user
from flask_login import LoginManager
from models import db,User
app=Flask(__name__)

app.config['SECRET_KEY'] = '9c6a7d0a3e4f2b1c8d5e9f7a2b3c4d6e'

# -----------------
# create database
# class Base(DeclarativeBase):
#     pass
#
# db = SQLAlchemy(model_class=Base)

migrate = Migrate()

def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sneha@localhost:5432/management'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(admin,url_prefix='/admin')
    app.register_blueprint(user,url_prefix='/user')
    migrate.init_app(app)
    return app

login_manager=LoginManager()
login_manager.init_app(app)

login_manager.login_view = "user.login"
login_manager.login_message = u" you have to login first! with correct credential!!"

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User,user_id)


@app.route('/')
def user_login():
    return redirect(url_for('user.login'))

if __name__ =='__main__':
    app = create_app()
    app.run(debug=True)