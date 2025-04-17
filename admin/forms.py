from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, SubmitField,TextAreaField,FileField
from wtforms.validators import DataRequired, Email, Length,  Regexp, EqualTo,ValidationError
import phonenumbers

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class AddUserForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    department = SelectField(
        'Department',
        validators=[DataRequired()],
        choices=[('', 'Select Department'),
                 ('AI/ML', 'AI/ML'),
                 ('Python', 'Python'),
                 ('QA', 'QA'),
                 ('UI/UX', 'UI/UX'),
                 ('Frontend', 'Frontend')
                ]
    )
    role = SelectField('Role', validators=[DataRequired()], choices=[('admin', 'admin'), ('employee', 'employee')],
                       default='employee')
    submit = SubmitField('Add User')

class UserDetailForm(FlaskForm):
    email = StringField('Email', render_kw={'readonly': True})
    department = StringField('Department', render_kw={'readonly': True})
    f_name = StringField('First Name', validators=[DataRequired()])
    l_name = StringField('Last Name', validators=[DataRequired()])

    phone = StringField('Phone',
                        validators=[Regexp(r'^[\d\-\+\(\) ]+$', message="Invalid phone number"), Length(max=17)])
    profile_image = FileField('Profile Image')
    submit = SubmitField('Submit')
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

    def validate_phone(self, phone1):
        try:
            p = phonenumbers.parse(phone1.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message="Passwords must match")])
    submit = SubmitField('Change Password')

class RaiseTicket(FlaskForm):
    ticket_label = StringField('Ticket Label', validators=[DataRequired()])
    ticket_question = TextAreaField('Ticket Question', validators=[DataRequired()])
    department = SelectField(
        'Department',
        validators=[DataRequired()],
        choices=[('ALL', 'ALL'),
                 ('AI/ML', 'AI/ML'),
                 ('Python', 'Python'),
                 ('QA', 'QA'),
                 ('UI/UX', 'UI/UX'),
                 ('Frontend', 'Frontend')
                 ]
    )



