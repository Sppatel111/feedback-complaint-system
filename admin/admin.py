import psycopg2
from flask import Blueprint, render_template, redirect, url_for, flash,request
from .forms import LoginForm, AddUserForm, UserDetailForm, ChangePasswordForm
from dotenv import load_dotenv
from models import db, User, Detail
from flask_login import login_user, current_user
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
        result = db.session.execute(db.select(User).where(User.email == email))
        user1= result.scalars().first()
        print(user1)
        if user1:
            if user1.password == password and user1.role == 'admin':
                login_user(user1)
                flash(f'Login successful for {email}', 'success')
                return redirect(url_for("admin.a_dashboard"))

        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('admin.login'))

    return render_template('admin_login.html', form=form)

# Dashboard routes
@admin.route('/dashboard')
def a_dashboard():

    return render_template("admin_dashboard.html")

@admin.route('/adduser', methods=['GET', 'POST'])
def add_user():
    form = AddUserForm()

    if form.validate_on_submit():

        new_user = User(
            email = form.email.data,
            password=form.password.data,
            department=form.department.data,
            role=form.role.data,
        )
        db.session.add(new_user)
        db.session.commit()

        new_detail = Detail(
            email=form.email.data,
        )
        db.session.add(new_detail)
        db.session.commit()

        flash("User registered successfully!", "success")
        return redirect(url_for("admin.a_dashboard"))

    return render_template("add_user.html",form=form)

@admin.route('/dashboard/managefeedback', methods=['GET', 'POST'])
def manage_feedback():
    return render_template("manage_feedback.html")

# Settings Route
@admin.route('/dashboard/settings', methods=['GET', 'POST'])
def a_settings():

    return render_template("admin_settings.html")

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
    return render_template("user_details.html", form=form)

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

    return render_template("change_password.html", form=form)

# Feedback routes
@admin.route('/dashboard/managefeedback/raisetickets', methods=['GET', 'POST'])
def raise_tickets():

    return render_template("raise_tickets.html")

@admin.route('/dashboard/managefeedback/viewfeedback', methods=['GET', 'POST'])
def view_feedback():

    return render_template("view_feedback.html")

@admin.route('/dashboard/managefeedback/assigntasks', methods=['GET', 'POST'])
def assign_tasks():

    return render_template("assign_tasks.html")