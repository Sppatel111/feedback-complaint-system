from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,EmailField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import email_validator


class LoginForm(FlaskForm):
    # email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class UserRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Create User')