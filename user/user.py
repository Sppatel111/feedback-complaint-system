from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy import or_
from .forms import LoginForm, UserDetailForm, ChangePasswordForm
from models import db, User, Detail, FeedbackTicket, FeedbackResponse, Task
from flask_login import login_user, current_user, logout_user, login_required
import os
import uuid

UPLOAD_FOLDER = 'user/static/assets/profiles/'
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
            if not user1.is_active:
                flash("This account is disabled. Please contact admin.", "danger")
                return redirect(url_for('user.login'))
            login_user(user1)

            flash(f'Login successful for {email}', 'success')
            return redirect(url_for("user.u_dashboard"))

        flash('Invalid credentials. Please try again.', 'danger')

    return render_template('user_login.html', form=form, current_user=current_user)


# logout Route
@user.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.login'))


# Dashboard Route
@user.route('/dashboard')
@login_required
def u_dashboard():
    return render_template("user_dashboard.html", current_user=current_user)


# Settings Route
@user.route('/dashboard/settings')
@login_required
def u_settings():
    return render_template("settings.html", current_user=current_user)

# User Details Route
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user.route('dashboard/settings/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@user.route('/dashboard/settings/user-details', methods=['GET', 'POST'])
@login_required
def u_details():
    form = UserDetailForm(obj=current_user.user_detail)
    form.email.data = current_user.email
    form.department.data = current_user.department
    if request.method == 'GET':
        form.f_name.data = current_user.user_detail.firstname
        form.l_name.data = current_user.user_detail.lastname
        form.phone.data = current_user.user_detail.phone_number
    # print("no")
    if form.validate_on_submit():
        # print("yes")
        if not current_user.user_detail:
            user_detail = Detail(email=current_user.email)
            db.session.add(user_detail)
        else:
            user_detail = current_user.user_detail

        user_detail.firstname = form.f_name.data
        user_detail.lastname = form.l_name.data
        user_detail.phone_number = form.phone.data
        # print(form.phone.data)
        file = form.profile_image.data
        # print(file)

        # using uuid
        if file or allowed_file(file.filename):
            if allowed_file(file.filename):
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                user_detail.profile_image = unique_filename
            else:
                flash("Unsupported file type. Please upload an image (png, jpg, jpeg, gif).","danger")
                return render_template("edit_details.html", form=form, current_user=current_user)

        db.session.commit()
        flash("Details updated successfully!", "success")
        return redirect(url_for("user.profile"))

    elif request.method == 'POST':
        flash("Invalid phone number.","danger")
        print(form.errors)
    return render_template("edit_details.html", form=form, current_user=current_user)


@user.route('/dashboard/settings/change-password', methods=['GET', 'POST'])
@login_required
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


@user.route('dashboard/manage-feedback', methods=['GET', 'POST'])
@login_required
def manage_feedback():
    return render_template("feedback_management.html", current_user=current_user)


@user.route('dashboard/manage-feedback/view-tickets', methods=['GET', 'POST'])
@login_required
def view_tickets():
    selected_status = request.args.get('status')

    if current_user.department:
        query = FeedbackTicket.query.filter(
            or_(
                FeedbackTicket.department_name == current_user.department,
                FeedbackTicket.department_name == 'ALL'
            )
        )
        if selected_status:
            query = query.filter(FeedbackTicket.ticket_status == selected_status)
        tickets = query.order_by(FeedbackTicket.created_at.desc()).all()
    else:
        tickets = []

    return render_template(
        'f_tickets.html',
        tickets=tickets,
        selected_status=selected_status,
        current_user=current_user
    )


# for the response in view tickets
@user.route('dashboard/manage-feedback/view-tickets/respond/<int:ticket_id>', methods=['POST'])
@login_required
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


@user.route('/dashboard/manage-feedback/view-tickets/ticket/<int:ticket_id>', methods=['GET'])
@login_required
def ticket_detail_response(ticket_id):
    ticket = FeedbackTicket.query.get(ticket_id)
    if ticket is None:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('user.view_tickets'))

    return render_template("ticket_detail_response.html", ticket=ticket)

@user.route('/dashboard/manage-feedback/task', methods=['GET'])
@login_required
def assigned_task():
    selected_status = request.args.get('status', '')

    query = Task.query.filter_by(assigned_to_email=current_user.email)

    if selected_status:
        query = query.filter_by(task_status=selected_status)

    tasks = query.all()

    status_colors = {
        'todo': 'orange',
        'in_progress': '#007bff',
        'in_review': '#6f42c1',
        'backlog': 'red',
        'on_hold': '#ffc107',
        'done': '#28a745',
        'completed': '#20c997',
    }

    status_options = {
        'high': ['todo', 'in_progress', 'backlog', 'in_review'],
        'medium': ['todo', 'in_progress', 'backlog', 'in_review', 'done'],
        'low': ['todo', 'in_progress', 'backlog', 'in_review', 'done', 'completed'],
    }

    return render_template(
        "tasks.html",
        tasks=tasks,
        status_colors=status_colors,
        status_options=status_options,
        selected_status=selected_status
    )


@user.route('/dashboard/manage-feedback/task/update/<int:task_id>', methods=['POST'])
@login_required
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
