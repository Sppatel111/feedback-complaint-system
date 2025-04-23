from flask import current_app, url_for
from flask_mail import Message
from models import Detail,FeedbackTicket

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=('Feedback and Complaint System Support', current_app.config['MAIL_USERNAME']),
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

- Feedback and Complaint System Support
'''

    mail = current_app.extensions['mail']
    mail.send(msg)


def send_assignment_email(assigned_email, ticket_id, task_details, deadline=None):
    # Get user details for personalized name
    user_detail = Detail.query.filter_by(email=assigned_email).first()
    if user_detail:
        firstname = user_detail.firstname or "User"
        lastname = user_detail.lastname or ""
        full_name = f"{firstname} {lastname}".strip()
    else:
        full_name = assigned_email

    # Get ticket info for context
    ticket = FeedbackTicket.query.get(ticket_id)
    ticket_title = ticket.ticket_label if ticket else f"Ticket #{ticket_id}"

    # Build email
    msg = Message('New Task Assignment',
                  sender=('Feedback and Complaint System Support', current_app.config['MAIL_USERNAME']),
                  recipients=[assigned_email])

    msg.body = f'''Hi {full_name},

You have been assigned a new task related to "{ticket_title}" (Ticket ID: {ticket_id}).

Task Details:
{task_details}

Deadline: {deadline or 'No deadline provided'}

Please log in to your ERP dashboard to view and manage the task.

-Feedback and Complaint System Support
'''

    mail = current_app.extensions['mail']
    mail.send(msg)


def send_welcome_email(email):
    # Get user details
    user_detail = Detail.query.filter_by(email=email).first()
    if user_detail:
        firstname = user_detail.firstname or "User"
        lastname = user_detail.lastname or ""
        full_name = f"{firstname} {lastname}".strip()
    else:
        full_name = email

    # Compose email
    msg = Message('Welcome to the Feedback and Complaint System',
                  sender=('Feedback and Complaint System Support', current_app.config['MAIL_USERNAME']),
                  recipients=[email])

    msg.body = f'''Hi {full_name},

Welcome to the ERP System! Your account has been successfully created.

You can now log in to the dashboard using your registered email address.

If you have any questions or issues, feel free to contact support.

We're excited to have you onboard!

- Feedback and Complaint System Support
'''

    mail = current_app.extensions['mail']
    mail.send(msg)


def send_account_status_email(email, is_active):
    # Fetch user's name
    user_detail = Detail.query.filter_by(email=email).first()
    if user_detail:
        firstname = user_detail.firstname or "User"
        lastname = user_detail.lastname or ""
        full_name = f"{firstname} {lastname}".strip()
    else:
        full_name = email

    # Compose message
    status_text = "enabled" if is_active else "disabled"
    msg = Message(
        subject=f"Your Feedback and Complaint System Account Has Been {status_text.capitalize()}",
        sender=('Feedback and Complaint System Support', current_app.config['MAIL_USERNAME']),
        recipients=[email]
    )

    msg.body = f"""Hi {full_name},

Your account on the ERP System has been {status_text} by the administrator.

If you believe this was a mistake or you have questions, please contact the system administrator.

- Feedback and Complaint System Support
"""

    mail = current_app.extensions['mail']
    mail.send(msg)