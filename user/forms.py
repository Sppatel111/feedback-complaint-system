from flask_wtf import FlaskForm
from wtforms import PasswordField, EmailField, StringField, SubmitField, FileField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError
import phonenumbers


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class UserDetailForm(FlaskForm):
    email = StringField('Email', render_kw={'readonly': True})
    department = StringField('Department', render_kw={'readonly': True})
    f_name = StringField('First Name', validators=[DataRequired()])
    l_name = StringField('Last Name', validators=[DataRequired()])
    # phone = StringField(
    #     'Phone Number',
    #     validators=[
    #         DataRequired(),
    #         Length(min=10, max=10, message="Phone number must be 10 digits"),
    #         Regexp(r'^\d{10}$', message="Phone number must contain only digits")
    #     ]
    # )
    phone = StringField('Phone',
                        validators=[Regexp(r'^[\d\-\+\(\) ]+$', message="Invalid phone number"),Length(max=17)])
    profile_image = FileField('Profile Image')
    submit = SubmitField('Submit')

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password',
                                                                                                 message="Passwords must match")])
    submit = SubmitField('Change Password')

class ComplaintForm(FlaskForm):
    title = StringField('Complaint Title', validators=[DataRequired(), Length(min=5, max=100)])
    department = SelectField('Department', choices=[
        ('hr', 'Human Resources'),
        ('it', 'IT'),
        ('finance', 'Finance'),
        ('procurement', 'Procurement'),
        ('tech','Tech'),
        ('admin', 'Administration')
    ])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    attachment = FileField('Attach File (optional)')