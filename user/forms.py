from flask_wtf import FlaskForm
from wtforms import PasswordField,EmailField,StringField,SubmitField,FileField
from wtforms.validators import DataRequired, Email, Length, Regexp,EqualTo

class LoginForm(FlaskForm):

    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class UserDetailForm(FlaskForm):
    email = StringField('Email', render_kw={'readonly': True})
    department = StringField('Department', render_kw={'readonly': True})
    f_name = StringField('First Name', validators=[DataRequired()])
    l_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField(
        'Phone Number',
        validators=[
            DataRequired(),
            Length(min=10, max=10, message="Phone number must be 10 digits"),
            Regexp(r'^\d{10}$', message="Phone number must contain only digits")
        ]
    )
    profile_image = FileField('Profile Image')
    submit = SubmitField('Submit')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message="Passwords must match")])
    submit = SubmitField('Change Password')