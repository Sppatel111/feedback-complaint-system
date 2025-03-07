from flask import Flask, redirect, url_for
from admin.admin import admin
from user.user import user

app=Flask(__name__)

app.config['SECRET_KEY'] = '9c6a7d0a3e4f2b1c8d5e9f7a2b3c4d6e'

app.register_blueprint(admin,url_prefix='/admin')
app.register_blueprint(user,url_prefix='/user')

@app.route('/')
def user_login():
    return redirect(url_for('user.login'))

if __name__ =='__main__':
    app.run(debug=True)