from flask import Blueprint, render_template, redirect, url_for, flash, session
from .forms import LoginForm, UserDetailForm,ChangePasswordForm
from dotenv import load_dotenv
from models import db, User,Detail
from flask_login import login_user,current_user,login_required

# Load environment variables
load_dotenv()

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
        result = db.session.execute(db.select(User).where(User.email == email))
        user1 = result.scalars().first()
        if user1:
            if user1.password == password and user1.role =='employee':
                login_user(user1)
                flash(f'Login successful for {email}', 'success')
                return redirect(url_for("user.u_dashboard"))

        # flash('Invalid credentials. Please try again.', 'danger')
        # return redirect(url_for('user.login'))

    return render_template('user_login.html', form=form)


# Dashboard Route
@user.route('/dashboard')
@login_required
def u_dashboard():
    # if not current_user:
    #     flash("Please login first.", "warning")
    #     return redirect(url_for("user.login"))

    return render_template("user_dashboard.html")


# Settings Route
@user.route('/dashboard/settings')
@login_required
def u_settings():
    # if not current_user:
    #     flash("Please login first.", "warning")
    #     return redirect(url_for("user.login"))

    return render_template("user_settings.html")


# User Details Route
@user.route('/dashboard/settings/userdetails', methods=['GET', 'POST'])
@login_required
def u_details():

    form = UserDetailForm(obj=current_user.user_detail)  # Prefill form data

    # Manually set non-editable fields
    form.email.data = current_user.email
    form.department.data = current_user.department

    if form.validate_on_submit():

        if not current_user.user_detail:
            user_detail = Detail(email=current_user.email)
            db.session.add(user_detail)
        else:
            user_detail = current_user.user_detail

        # Update details
        user_detail.firstname = form.f_name.data
        user_detail.lastname = form.l_name.data
        user_detail.phone_number = form.phone.data

        db.session.commit()
        flash("Details updated successfully!", "success")
        return redirect(url_for("user.u_details"))

    return render_template("user_details.html", form=form)

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

    return render_template("change_password.html", form=form)
