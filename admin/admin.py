import psycopg2
from flask import Blueprint, render_template, redirect, url_for, flash, request
from .forms import LoginForm, AddUserForm, UserDetailForm, ChangePasswordForm, RaiseTicket
from dotenv import load_dotenv
from models import db, User, Detail, FeedbackTicket, FeedbackResponse,Task
from flask_login import login_user, current_user, login_required, logout_user
import os

load_dotenv()
admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static")


@admin.route('/', methods=['GET', 'POST'])
@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        admin1 = User.query.filter_by(email=email, role='admin').first()

        if admin1 and admin1.password == password:
            login_user(admin1)
            flash(f'Login successful for {email}', 'success')
            return redirect(url_for("admin.a_dashboard"))

        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('admin.login'))

    return render_template('admin_login.html', form=form, current_user=current_user)


@admin.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


# Dashboard routes
@admin.route('/dashboard')
def a_dashboard():
    return render_template("admin_dashboard.html", current_user=current_user)


@admin.route('/adduser', methods=['GET', 'POST'])
def add_user():
    form = AddUserForm()

    if form.validate_on_submit():

        new_user = User(
            email=form.email.data,
            password=form.password.data,
            department=form.department.data,
            role=form.role.data,
        )
        result=db.session.execute(db.select(User.email))
        if not form.email.data in result.scalars():
            db.session.add(new_user)
            db.session.commit()

            new_detail = Detail(
                email=form.email.data,
            )
            db.session.add(new_detail)
            db.session.commit()

            flash("User registered successfully!", "success")
            return redirect(url_for("admin.a_dashboard"))
        print("nope")
        flash("User already registered!!! ", "danger")
    return render_template("add_user.html", form=form, current_user=current_user)


@admin.route('/dashboard/manage-feedback', methods=['GET', 'POST'])
def manage_feedback():
    return render_template("manage_feedback.html", current_user=current_user)


# Settings Route
@admin.route('/dashboard/settings', methods=['GET', 'POST'])
def a_settings():
    return render_template("settings.html", current_user=current_user)


@admin.route('/dashboard/settings/admindetails', methods=['GET', 'POST'])
def a_details():
    form = UserDetailForm(obj=current_user.user_detail)

    form.email.data = current_user.email
    form.department.data = current_user.department

    if form.validate_on_submit():
        print("Form Submitted!")
        print(f"First Name: {form.f_name.data}, Last Name: {form.l_name.data}, Phone: {form.phone.data}")
        if not current_user.user_detail:
            user_detail = Detail(email=current_user.email)
            db.session.add(user_detail)
        else:
            user_detail = current_user.user_detail

        print(f"Before update: {user_detail.firstname}, {user_detail.lastname}, {user_detail.phone_number}")

        # Update details
        user_detail.firstname = form.f_name.data
        user_detail.lastname = form.l_name.data
        user_detail.phone_number = form.phone.data

        print(f"After update: {user_detail.firstname}, {user_detail.lastname}, {user_detail.phone_number}")

        db.session.commit()
        flash("Details updated successfully!", "success")
        return redirect(url_for("admin.a_settings"))
    else:
        print("Else form not submitted")
    return render_template("user_details.html", form=form, current_user=current_user)


@admin.route('/dashboard/settings/change-password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data

        if current_password == current_user.password:
            current_user.password = new_password
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin.a_settings'))
        else:
            flash('Incorrect current password.', 'danger')

    return render_template("change_password.html", form=form, current_user=current_user)


# you have ti ckeck logic pending
@admin.route('/dashboard/setting/view-profile', methods=['GET', 'POST'])
def profile():
    return render_template("user_profile.html", current_user=current_user)


# Feedback routes
@admin.route('/dashboard/managefeedback/raisetickets', methods=['GET', 'POST'])
def raise_tickets():
    form = RaiseTicket()
    if form.validate_on_submit():
        new_ticket = FeedbackTicket(
            user_email=current_user.email,
            ticket_label=form.ticket_label.data,
            question=form.ticket_question.data,
            department_name=form.department.data
        )

        db.session.add(new_ticket)
        db.session.commit()
        flash('Successfully created ticket!!', 'success')
        return redirect(url_for('admin.manage_feedback'))

    return render_template("raise_tickets.html", form=form, current_user=current_user)


### user feedback
@admin.route('/dashboard/managefeedback/viewfeedback', methods=['GET', 'POST'])
def view_feedback():
    departments = db.session.query(FeedbackTicket.department_name).distinct().all()
    department_names = [dept[0] for dept in departments]
    selected_department = request.args.get('department')

    if selected_department:
        feedback_responses = FeedbackResponse.query.join(FeedbackTicket).filter(
            FeedbackTicket.department_name == selected_department
        ).all()
    else:
        feedback_responses = FeedbackResponse.query.all()

    return render_template("view_feedback.html", feedback_responses=feedback_responses,
                           department_names=department_names, selected_department=selected_department)

### need check below two function
###  ticket detail and user responses on it
@admin.route('/dashboard/managefeedback/ticket/<int:ticket_id>', methods=['GET'])
def view_ticket_details(ticket_id):
    ticket = FeedbackTicket.query.get(ticket_id)
    if ticket is None:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('admin.view_feedback'))

    return render_template("ticket_details.html", ticket=ticket)

@admin.route('/dashboard/managefeedback/ticket/<int:ticket_id>/respond', methods=['POST'])
def respond_to_ticket(ticket_id):
    return redirect(url_for('admin.view_ticket_details', ticket_id=ticket_id))


###Assign task
@admin.route('/dashboard/managefeedback/assigntasks', methods=['GET', 'POST'])
def assign_tasks():
    all_task=FeedbackTicket.query.all()
    return render_template("assign_tasks.html",all_task=all_task)


# @admin.route('/dashboard/managefeedback/assigntasks/<int:ticket_id>',methods=['GET','POST'])
# def assign_user(ticket_id):
#     ticket1 = FeedbackTicket.query.get(ticket_id)
#     if ticket1 is None:
#         flash('Ticket not found.', 'danger')
#     return render_template("assign_user.html",ticket=ticket1)

@admin.route('/dashboard/managefeedback/assigntasks/<int:ticket_id>', methods=['GET', 'POST'])
def assign_user(ticket_id):
    ticket1 = FeedbackTicket.query.get(ticket_id)
    if ticket1 is None:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('admin.assign_tasks'))

    if request.method == 'POST':
        assigned_email = request.form.get('assigned_email')
        details = request.form.get('details')
        deadline = request.form.get('deadline')

        if assigned_email and details:
            new_task = Task(ticket_id=ticket_id, assigned_to_email=assigned_email, details=details, deadline=deadline)
            db.session.add(new_task)
            db.session.commit()
            flash('User assigned to the task successfully!', 'success')
            return redirect(url_for('admin.assign_tasks'))


    all_users = User.query.all()
    return render_template("assign_user.html", ticket=ticket1, all_users=all_users)


# @admin.route('/dashboard/managefeedback/assigntasks/<int:ticket_id>',methods=['GET','POST'])
# def ticket_status(ticket_id):
#     ticket = FeedbackTicket.query.get(ticket_id)
#     if ticket is None:
#         flash('Ticket not found.', 'danger')
#     return render_template("",ticket=ticket)