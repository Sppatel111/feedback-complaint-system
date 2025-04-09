from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy import or_

from .forms import LoginForm, UserDetailForm, ChangePasswordForm
from models import db, User, Detail, FeedbackTicket, FeedbackResponse, Task
from flask_login import login_user, current_user, logout_user
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'user/static/assets/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Flask Blueprint for user-related routes
user = Blueprint("user", __name__, template_folder="templates", static_folder="static")


# Login Route
@user.route('/', methods=['GET', 'POST'])
@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user1 = User.query.filter_by(email=email, role='employee').first()

        if user1 and user1.password == password:
            login_user(user1)

            flash(f'Login successful for {email}', 'success')
            return redirect(url_for("user.u_dashboard"))

        flash('Invalid credentials. Please try again.', 'danger')

    return render_template('user_login.html', form=form, current_user=current_user)

#logout Route
@user.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.login'))


# Dashboard Route
@user.route('/dashboard')
def u_dashboard():
    return render_template("user_dashboard.html", current_user=current_user)


# Settings Route
@user.route('/dashboard/settings')
def u_settings():
    return render_template("settings.html", current_user=current_user)


# User Details Route
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user.route('/dashboard/settings/userdetails', methods=['GET', 'POST'])
def u_details():
    form = UserDetailForm(obj=current_user.user_detail)
    form.email.data = current_user.email
    form.department.data = current_user.department

    if form.validate_on_submit():
        if not current_user.user_detail:
            user_detail = Detail(email=current_user.email)
            db.session.add(user_detail)
        else:
            user_detail = current_user.user_detail


        user_detail.firstname = form.f_name.data
        user_detail.lastname = form.l_name.data
        user_detail.phone_number = form.phone.data
        file = form.profile_image.data
        print(file)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            user_detail.profile_image = filename

        db.session.commit()
        flash("Details updated successfully!", "success")
        return redirect(url_for("user.u_details"))

    return render_template("user_details.html", form=form, current_user=current_user)


# you have to check
@user.route('/dashboard/setting/view-profile', methods=['GET', 'POST'])
def profile():
    profile = db.session.execute(db.select(User).where(User.email == current_user.email))
    profile_detail = db.session.execute(db.select(Detail).where(Detail.email == current_user.email))
    result = profile.scalars().all()
    print(result)
    return render_template("user_profile.html", current_user=current_user)


@user.route('/dashboard/settings/change-password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data

        if current_password == current_user.password:
            current_user.password = new_password
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('user.u_dashboard'))
        else:
            flash('Incorrect current password.', 'danger')

    return render_template("change_password.html", form=form, current_user=current_user)


@user.route('dashboard/feedback', methods=['GET', 'POST'])
def manage_feedback():
    return render_template("feedback_management.html", current_user=current_user)


@user.route('dashboard/feedback/view-tickets', methods=['GET', 'POST'])
def view_tickets():
    if current_user.department:
        tickets = FeedbackTicket.query.filter(or_(FeedbackTicket.department_name == current_user.department,FeedbackTicket.department_name =='ALL')).all()
    else:
        tickets=[]
    return render_template('f_tickets.html', tickets=tickets, current_user=current_user)

# for the response in view tickets
@user.route('dashboard/respond/<int:ticket_id>', methods=['POST'])
def respond_to_ticket(ticket_id):
    response_text = request.form.get('response')
    if response_text:
        new_response = FeedbackResponse(
            ticket_id=ticket_id,
            user_email=current_user.email,
            response=response_text
        )
        db.session.add(new_response)
        db.session.commit()
        flash('Your response has been submitted!', 'success')
    else:
        flash('Response cannot be empty.', 'danger')

    return redirect(url_for('user.view_tickets'))

@user.route('/dashboard/ticket/<int:ticket_id>', methods=['GET'])
def ticket_detail_response(ticket_id):
    ticket = FeedbackTicket.query.get(ticket_id)
    if ticket is None:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('user.view_tickets'))

    return render_template("ticket_detail_response.html", ticket=ticket)


@user.route('/dashboard/feedback/task', methods=['GET'])
def assigned_task():
    tasks = Task.query.filter_by(assigned_to_email=current_user.email).all()

    status_colors = {
        'todo': 'orange',
        'in_progress': '#007bff',
        'in_review': '#6f42c1',
        'backlog': 'red',
        'on_hold': '#ffc107',
        'done': '#28a745',
        'completed': '#20c997',
    }

    return render_template("tasks.html", tasks=tasks, status_colors=status_colors)



@user.route('/dashboard/feedback/task/update/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    task = Task.query.get(task_id)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('user.assigned_task'))

    if task.ticket.ticket_status == 'closed':
        flash('Cannot update task status. The ticket is closed.', 'warning')
        return redirect(url_for('user.assigned_task'))

    new_status = request.form.get('task_status')
    task.task_status = new_status
    db.session.commit()
    flash('Task status updated successfully!', 'success')
    return redirect(url_for('user.assigned_task'))
