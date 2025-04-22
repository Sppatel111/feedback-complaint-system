from flask import current_app, url_for
from flask_mail import Message
from models import Detail

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@example.com',
                  recipients=[user.email])

    user_detail = Detail.query.filter_by(email=user.email).first()
    if user_detail:
        firstname = user_detail.firstname or "User"
        lastname = user_detail.lastname or ""
        full_name = f"{firstname} {lastname}".strip()
    else:
        full_name = user.email
    msg.body = f'''Hi {full_name},

To reset your password, click the link below:

{url_for('user.reset_token', token=token, _external=True)}

If you did not request a password reset, please ignore this email.

- ERP System Support
'''

    mail = current_app.extensions['mail']
    mail.send(msg)
