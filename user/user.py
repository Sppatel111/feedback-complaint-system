import sqlalchemy
from flask import Blueprint, render_template, redirect, url_for, flash, request
from .forms import LoginForm, UserDetailForm, ChangePasswordForm
from models import db, User, Detail, FeedbackTicket, FeedbackResponse
from flask_login import login_user, current_user, logout_user

# Flask Blueprint for user-related routes
user = Blueprint("user", __name__, template_folder="templates", static_folder="static")


# Login Route
# @user.route('/', methods=['GET', 'POST'])
# @user.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#
#     if form.validate_on_submit():
#         email = form.email.data
#         password = form.password.data
#         result = db.session.execute(db.select(User).where(User.email == email))
#         user1 = result.scalars().first()
#         print("yep")
#         print(user1)
#         if user1:
#             if user1.password == password and user1.role =='employee':
#                 login_user(user1)
#                 flash(f'Login successful for {email}', 'success')
#                 return redirect(url_for("user.u_dashboard"))
#         print('nope')
#         # flash('Invalid credentials. Please try again.', 'danger')
#         # return redirect(url_for('user.login'))
#
#     return render_template('user_login.html', form=form,current_user=current_user)

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
    return render_template("user_settings.html", current_user=current_user)


# User Details Route
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
        # Update details
        user_detail.firstname = form.f_name.data
        user_detail.lastname = form.l_name.data
        user_detail.phone_number = form.phone.data

        db.session.commit()
        flash("Details updated successfully!", "success")
        return redirect(url_for("user.u_details"))

    return render_template("user_details.html", form=form, current_user=current_user)


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


@user.route('dashboard/view', methods=['GET', 'POST'])
def view_tickets():
    if current_user.department:
        tickets = FeedbackTicket.query.filter_by(department_name=current_user.department).all()
    else:
        tickets = []
    return render_template('f_tickets.html', tickets=tickets, current_user=current_user)


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

