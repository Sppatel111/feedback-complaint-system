from datetime import datetime
import psycopg2
from flask import Blueprint, render_template, redirect, url_for, flash, request
from .forms import LoginForm, AddUserForm, UserDetailForm, ChangePasswordForm, RaiseTicket, ResetPasswordForm, RequestResetForm
from dotenv import load_dotenv
from models import db, User, Detail, FeedbackTicket, FeedbackResponse, Task,Complaint,ComplaintResponse
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.utils import secure_filename
import os
import uuid
from sqlalchemy import func, or_
from utils import send_reset_email, send_assignment_email, send_welcome_email, send_account_status_email
from collections import Counter
import plotly.graph_objects as go
import plotly.io as pio

# UPLOAD_FOLDER = 'user/static/assets/'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'user/static/assets/profiles/'
ATTACHMENT_FOLDER='user/static/assets/attachments/'
ALLOWED_EXTENSIONS = {
    'profile':['png', 'jpg', 'jpeg', 'gif'],
    'attachment':['pdf','jpg','jpeg']
    }

def allowed_file(filename,category):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[category]

load_dotenv()
admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

# Login Route
@admin.route('/', methods=['GET', 'POST'])
@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        admin1 = User.query.filter_by(email=email, role='admin').first()

        if admin1 and admin1.password == password:
            if not admin1.is_active:
                flash("This account is disabled. Please contact admin.", "danger")
                return redirect(url_for('admin.login'))
            login_user(admin1)
            flash(f'Login successful for {email}', 'success')
            return redirect(url_for("admin.a_dashboard"))

        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('admin.login'))

    return render_template('admin_login.html', form=form, current_user=current_user)

# Logout Route
@admin.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


#Dashboard routes
# @admin.route('/dashboard')
# @login_required
# def a_dashboard():
#     return render_template("admin_dashboard.html", current_user=current_user)

@admin.route('/dashboard')
@login_required
def a_dashboard():
    users = User.query.all()
    pio.templates.default = "plotly_white"
    # Shared Chart Layout
    chart_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family='"Segoe UI", sans-serif',
            color='black',
            size=14
        ),
        height=340,
        width=380,
        margin=dict(t=30, b=30, l=10, r=10),
        showlegend=True,
    )

    # --- Active vs Disabled Users Pie Chart ---
    active_status_counts = Counter('Active' if u.is_active else 'Disabled' for u in users)
    active_status_chart = go.Figure(data=[go.Pie(
        labels=list(active_status_counts.keys()),
        values=list(active_status_counts.values()),
        marker=dict(colors=['#D3D3D3', '#E5E4E2']),
        textinfo='percent+label',
        hole=0.3
    )])
    active_status_chart.update_layout(chart_layout)

    # --- Department Wise User Count Bar Chart ---
    department_counts = Counter(u.department if u.department else 'No Department' for u in users)
    department_chart = go.Figure(data=[go.Bar(
        x=list(department_counts.keys()),
        y=list(department_counts.values()),
        name='Department',
        marker_color='#C9E9D2'  # Pastel Blue
    )])
    department_chart.update_layout(chart_layout)

    # --- Role Wise (Admin vs Employee) Pie Chart ---
    role_counts = Counter(u.role for u in users)
    role_chart = go.Figure(data=[
        go.Bar(
            x=list(role_counts.values()),
            y=list(role_counts.keys()),
            orientation='h',
            name='Role',
            marker_color=['#FFCFCF', '#FFE2E2']
        )
    ])
    role_chart.update_layout(chart_layout)

    # role_chart = go.Figure(data=[go.Pie(
    #     labels=list(role_counts.keys()),
    #     values=list(role_counts.values()),
    #     marker=dict(colors=['#FFCFCF','#FFE2E2']),
    #     textinfo='percent+label',
    #     hole=0.3
    # )])
    # role_chart.update_layout(chart_layout)
    active_status_html = pio.to_html(active_status_chart, full_html=False)
    department_html = pio.to_html(department_chart, full_html=False)
    role_html = pio.to_html(role_chart, full_html=False)
    return render_template("admin_dashboard.html", current_user=current_user,
                                active_status_html = active_status_html,
                                department_html = department_html,
                                role_html = role_html)


# Manage User Route (add user,view user,edit user,active mode )
@admin.route('/manage-user', methods=['GET', 'POST'])
def manage_users():
    query = request.args.get('query', '', type=str)

    ##page
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = 4
    users = User.query.join(Detail)
    if query:
        query = query.lower()
        status_filter = None

        if query in ['active', 'enabled']:
            status_filter = True
        elif query in ['disabled', 'inactive']:
            status_filter = False

        filters = [
            Detail.firstname.ilike(f"%{query}%"),
            Detail.lastname.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%"),
            User.department.ilike(f"%{query}%"),
            User.role.ilike(f"%{query}%")
        ]

        if status_filter is not None:
            filters.append(User.is_active == status_filter)

        users = users.filter(or_(*filters))
    # pagination
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            users = users.filter(User.created_at.between(start_date, end_date))
        except ValueError:
            pass

    pagination = users.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    users = pagination.items

    return render_template("admin_manage_users.html", users=users, pagination=pagination,
        start_date=start_date_str,
        end_date=end_date_str)

# Add user Route
@admin.route('/manage-user/adduser', methods=['GET', 'POST'])
@login_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            password=form.password.data,
            department=form.department.data,
            role=form.role.data,
        )
        result = db.session.execute(db.select(User.email))
        if not form.email.data in result.scalars():
            db.session.add(new_user)
            db.session.commit()

            new_detail = Detail(
                email=form.email.data,
            )
            db.session.add(new_detail)
            db.session.commit()
            send_welcome_email(form.email.data)

            flash("User registered successfully!", "success")
            return redirect(url_for("admin.manage_users"))
        # print("nope")
        flash("User already registered!!! ", "danger")
    return render_template("add_user.html", form=form, current_user=current_user)

# View user Route
@admin.route('/manage-user/user/<email>')
@login_required
def view_user(email):
    user = User.query.filter_by(email=email).first_or_404()
    tasks = Task.query.filter_by(assigned_to_email=email).join(FeedbackTicket).order_by(Task.created_at.desc()).all()
    return render_template('admin_view_user.html', user=user, tasks=tasks)

@admin.route('/manage-user/user/assign-user/<int:ticket_id>/<email>', methods=['GET', 'POST'])
@login_required
def manage_user_assign_detail(ticket_id,email):
    ticket1 = FeedbackTicket.query.get(ticket_id)
    user_tasks = Task.query.filter_by(ticket_id=ticket_id, assigned_to_email=email).all()

    if not user_tasks:
        flash('No tasks found for this user on this ticket.', 'warning')

    if ticket1 is None:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('admin.manage_user_assign_detail'))

    return render_template("manage_user_assign_task_detail.html", ticket=ticket1,tasks=user_tasks)

# Edit User Route
@admin.route('/manage-user/edit-user/<email>', methods=['GET', 'POST'])
@login_required
def edit_user(email):
    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        user.role = request.form['role']
        user.department = request.form['department']
        user.user_detail.firstname = request.form['firstname']
        user.user_detail.lastname = request.form['lastname']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin_edit_user.html', user=user)

# User Status
@admin.route('/manage-user/toggle-user/<email>')
@login_required
def toggle_user_status(email):
    user = User.query.filter_by(email=email).first_or_404()
    user.is_active = not user.is_active
    db.session.commit()
    send_account_status_email(user.email, user.is_active)
    flash(f"User {'enabled' if user.is_active else 'disabled'} successfully!", 'info')
    return redirect(url_for('admin.manage_users'))


# Settings Route
@admin.route('/dashboard/settings', methods=['GET', 'POST'])
@login_required
def a_settings():
    return render_template("settings.html", current_user=current_user)


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Admin detail Route
@admin.route('/dashboard/settings/admindetails', methods=['GET', 'POST'])
@login_required
def a_details():
    form = UserDetailForm(obj=current_user.user_detail)
    form.email.data = current_user.email
    form.department.data = current_user.department
    if request.method == 'GET':
        form.f_name.data = current_user.user_detail.firstname
        form.l_name.data = current_user.user_detail.lastname
        form.phone.data = current_user.user_detail.phone_number

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
        # print(file)

        # using uuid
        if file or allowed_file(file.filename,'profile'):
            if allowed_file(file.filename,'profile'):
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                user_detail.profile_image = unique_filename
            else:
                flash("Unsupported file type. Please upload an image (png, jpg, jpeg, gif).", "danger")
                return render_template("edit_details.html", form=form, current_user=current_user)

        db.session.commit()
        flash("Details updated successfully!", "success")
        return redirect(url_for("admin.profile"))
    elif request.method == 'POST':
        flash("Invalid phone number.","danger")
        # print(form.errors)
    return render_template("edit_details.html", form=form, current_user=current_user)

# Change Password Route
@admin.route('/dashboard/settings/change-password', methods=['GET', 'POST'])
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
            return redirect(url_for('admin.a_dashboard'))
        else:
            flash('Incorrect current password.', 'danger')

    return render_template("change_password.html", form=form, current_user=current_user)


# View Profile Route
@admin.route('/dashboard/setting/view-profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template("profile.html", user=current_user)

# Manage Feedback Route(raise ticket,view feedback, assign task)
# @admin.route('/manage-feedback', methods=['GET', 'POST'])
# @login_required
# def manage_feedback():
#     return render_template("manage_feedback.html", current_user=current_user)


# Manage Feedback Route(raise ticket,view feedback, assign task)
@admin.route('/manage-feedback', methods=['GET', 'POST'])
@login_required
def manage_feedback():
    tickets = FeedbackTicket.query.all()
    tasks = Task.query.all()
    pio.templates.default = "plotly_white"
    # Shared Chart Layout
    chart_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family='"Segoe UI", sans-serif',
            color='black',
            size=14
        ),
        height=340,
        width=380,
        margin=dict(t=30, b=30, l=10, r=10),
        showlegend=True,
    )
    # --- Tickets Status Pie Chart ---
    ticket_status_counts = Counter(t.ticket_status for t in tickets)
    ticket_chart = go.Figure(data=[go.Pie(
        labels=list(ticket_status_counts.keys()),
        values=list(ticket_status_counts.values()),
        marker=dict(colors=['#C9E9D2', '#F9E79F', '#D5DBDB']),
        # Pastel Teal, Pastel Yellow, Pastel Grey
        textinfo='percent+label',
        hole=0.4
    )])
    ticket_chart.update_layout(chart_layout)

    # --- Department-wise Tickets Bar Chart ---
    f_department_counts = Counter(t.department_name if t.department_name else "No Department" for t in tickets)

    f_department_chart = go.Figure(data=[go.Bar(
        x=list(f_department_counts.keys()),
        y=list(f_department_counts.values()),
        name='Tickets',
        marker_color='#C9E9D2'
    )])
    f_department_chart.update_layout(chart_layout)

    # --- Department-wise Assigned Users from Tasks ---
    assigned_task_department_counts = Counter(
        t.ticket.department_name if t.assigned_to_email else "Unassigned"
        for t in tasks
    )
    assigned_task_department_chart = go.Figure(data=[go.Bar(
        x=list(assigned_task_department_counts.keys()),
        y=list(assigned_task_department_counts.values()),
        name='assigned',
        marker_color='#FAD7A0'
        # Pastel Peach
    )])
    assigned_task_department_chart.update_layout(chart_layout)

    ticket_chart_html = pio.to_html(ticket_chart, full_html=False)
    f_department_html = pio.to_html(f_department_chart, full_html=False)
    assigned_task_department_html = pio.to_html(assigned_task_department_chart, full_html=False)
    return render_template("manage_feedback.html", current_user=current_user,
                           ticket_chart_html=ticket_chart_html,
                           f_department_html=f_department_html,
                           assigned_task_department_html=assigned_task_department_html,)


# Raise ticket routes
@admin.route('/manage-feedback/raise-tickets', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('admin.assign_tasks'))

    return render_template("raise_tickets.html", form=form, current_user=current_user)


# View feedback Response Route
@admin.route('manage-feedback/view-feedback', methods=['GET', 'POST'])
@login_required
def view_feedback():
    departments = db.session.query(FeedbackTicket.department_name).distinct().all()
    department_names = [dept[0] for dept in departments]
    selected_department = request.args.get('department')
    ##page
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = 2
    feedback_responses = FeedbackResponse.query.join(FeedbackTicket)
    if selected_department:
        feedback_responses = FeedbackResponse.query.join(FeedbackTicket).filter(
            FeedbackTicket.department_name == selected_department
        ).order_by(FeedbackResponse.created_at.desc())
    # pagination
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            feedback_responses = feedback_responses.filter(FeedbackResponse.created_at.between(start_date, end_date))
        except ValueError:
            pass
    pagination = feedback_responses.order_by(FeedbackResponse.created_at.desc()).paginate(page=page, per_page=per_page)
    feedback_responses = pagination.items

    return render_template("view_feedback.html", feedback_responses=feedback_responses,
                           pagination=pagination,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           department_names=department_names, selected_department=selected_department)



# View ticket and response detail Route
### need check below two function
###  ticket detail and user responses on it
@admin.route('manage-feedback/ticket/<int:ticket_id>', methods=['GET'])
@login_required
def view_ticket_details(ticket_id):
    ticket = FeedbackTicket.query.get(ticket_id)
    if ticket is None:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('admin.view_feedback'))

    return render_template("ticket_details.html", ticket=ticket)


# Assign task Route (assign user,view task users)
@admin.route('/manage-feedback/assign-tasks', methods=['GET', 'POST'])
@login_required
def assign_tasks():
    selected_status = request.args.get('status')
    ##page
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = 3

    if selected_status:
        all_task = FeedbackTicket.query.filter_by(ticket_status=selected_status
                                                  ).order_by(FeedbackTicket.created_at.desc())
        # pagination
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = end_date.replace(hour=23, minute=59, second=59)
                all_task = all_task.filter(FeedbackTicket.created_at.between(start_date, end_date))
            except ValueError:
                pass  # Ignore invalid date formats silently
        pagination = all_task.paginate(page=page, per_page=per_page)
        all_task = pagination.items
    else:
        all_task = FeedbackTicket.query.order_by(FeedbackTicket.created_at.desc())
        # pagination
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = end_date.replace(hour=23, minute=59, second=59)
                all_task = all_task.filter(FeedbackTicket.created_at.between(start_date, end_date))
            except ValueError:
                pass  # Ignore invalid date formats silently
        pagination = all_task.paginate(page=page, per_page=per_page)
        all_task = pagination.items

    status_colors = {
        'open': '#17a2b8',
        'closed': '#28a745',
        'in_progress': '#ffc107'
    }
    return render_template("assign_tasks.html", all_task=all_task, status_colors=status_colors,
                           pagination=pagination,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           selected_status=selected_status)

# Ticket status change
@admin.route('manage-feedback/assign-tasks/status/<int:ticket_id>', methods=['POST'])
@login_required
def update_ticket_status(ticket_id):
    ticket = FeedbackTicket.query.get(ticket_id)
    if ticket:
        new_status = request.form.get('ticket_status')
        ticket.ticket_status = new_status
        db.session.commit()
        flash('Ticket status updated successfully!', 'success')
    else:
        flash('Ticket not found!', 'danger')
    return redirect(url_for('admin.assign_tasks'))

# Assign User Route
@admin.route('manage-feedback/assign-tasks/assign-user/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def assign_user(ticket_id):
    ticket1 = FeedbackTicket.query.get(ticket_id)
    if ticket1 is None:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('admin.assign_tasks'))

    #department from query param
    selected_department = request.args.get('department')

    #all departments for the dropdown
    departments = db.session.query(User.department).distinct().all()
    departments = [d[0] for d in departments if d[0]]

    #Filter users by department
    if selected_department:
        all_users = User.query.filter_by(department=selected_department).all()
    else:
        all_users = []

    if request.method == 'POST':
        assigned_email = request.form.get('assigned_email')
        details = request.form.get('details')
        deadline = request.form.get('deadline')

        if ticket1.ticket_status == 'closed':
            flash('This ticket is closed. You cannot assign new tasks.', 'danger')
            return redirect(url_for('admin.assign_user', ticket_id=ticket_id, department=selected_department))

        if assigned_email and details:
            new_task = Task(ticket_id=ticket_id, assigned_to_email=assigned_email, details=details, deadline=deadline)
            db.session.add(new_task)
            db.session.commit()
            # Send assignment email
            send_assignment_email(assigned_email, ticket_id, details, deadline)
            flash('User assigned to the task successfully!', 'success')
            return redirect(url_for('admin.assign_tasks'))

    return render_template("assign_user.html", ticket=ticket1, all_users=all_users, departments=departments,
                           selected_department=selected_department)

# View Task Users
@admin.route('manage-feedback/assign-tasks/task-workers/<int:ticket_id>')
@login_required
def view_task_workers(ticket_id):
    ticket = FeedbackTicket.query.get_or_404(ticket_id)

    selected_status = request.args.get('status', '')
        ##page
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = 2

    query = Task.query.filter_by(ticket_id=ticket_id)

    if selected_status:
        query = query.filter_by(task_status=selected_status)
    task_workers = query
    # pagination
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            task_workers= task_workers.filter(Task.deadline.between(start_date, end_date))
        except ValueError:
            pass  # Ignore invalid date formats silently

    pagination = task_workers.paginate(page=page, per_page=per_page)
    task_workers= pagination.items

    # status_colors = {
    #     'todo': 'orange',
    #     'in_progress': '#007bff',
    #     'in_review': '#6f42c1',
    #     'backlog': 'red',
    #     'on_hold': '#ffc107',
    #     'done': '#28a745',
    #     'completed': '#20c997',
    # }
    status_colors = {
        'todo': 'orange',
        'in_progress': '#17a2b8',
        'in_review': '#AA60C8',
        'backlog': '#CC2B52',
        'on_hold': '#ffc107',
        'done': '#28a745',
        'completed': '#6BCB77',
    }

    return render_template('admin_view_task_workers.html', ticket=ticket, task_workers=task_workers, pagination=pagination,
        start_date=start_date_str,
        end_date=end_date_str, status_colors=status_colors, selected_status=selected_status)

# update task status and priority
@admin.route('manage-feedback/assign-tasks/task-workers/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task_status_priority(task_id):
    task = Task.query.get_or_404(task_id)

    new_status = request.form.get('task_status')
    new_priority = request.form.get('priority')

    if new_status and new_status != task.task_status:
        task.task_status = new_status
        flash("Task status updated successfully.", "info")

    if new_priority and new_priority != task.priority:
        task.priority = new_priority
        flash("Task priority updated successfully.", "info")

    deadline_str = request.form.get('deadline')
    if deadline_str:
        try:
            task.deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            flash("Deadline updated successfully.", "info")
        except ValueError:
            flash("Invalid date format", "danger")

    db.session.commit()
    return redirect(request.referrer or url_for('admin.dashboard'))


# compliant Routes
@admin.route('/complaint-center', methods=['GET', 'POST'])
@login_required
def manage_complaint():
    # marker_color = '#FAD7A0'
    # marker_color='#C9E9D2'
    # marker = dict(colors=['#C9E9D2', '#F9E79F', '#D5DBDB']),
    complaints = Complaint.query.all()

    # Set default Plotly template
    pio.templates.default = "plotly_white"

    # Shared Chart Layout
    chart_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',  # Keep transparent inside plot (fix gradient issue)
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family='"Segoe UI", sans-serif',
            color='black',
            size=14
        ),
        height=350,
        width=420,
        margin=dict(t=30, b=30, l=10, r=10),
        showlegend=True,
    )
    # --- Complaint Status Pie Chart ---
    complaint_status_counts = Counter(c.status for c in complaints)
    complaint_status_chart = go.Figure(data=[go.Pie(
        labels=list(complaint_status_counts.keys()),
        values=list(complaint_status_counts.values()),
        marker=dict(colors=['#FAD7A0', '#FFB9B9', '#C9E9D2']),
        textinfo='percent+label',
        hole=0.4
    )])
    complaint_status_chart.update_layout(chart_layout)

    # --- Department-wise Complaints Bar Chart ---
    complaint_department_counts = Counter(c.department if c.department else "No Department" for c in complaints)
    complaint_department_chart = go.Figure(data=[go.Bar(
        x=list(complaint_department_counts.keys()),
        y=list(complaint_department_counts.values()),
        name='Department',
        marker_color='#A6D0DD'

    )])
    complaint_department_chart.update_layout(chart_layout)
    complaint_status_html = pio.to_html(complaint_status_chart, full_html=False)
    complaint_department_html = pio.to_html(complaint_department_chart, full_html=False)
    complaint_counts = db.session.query(
        Complaint.status, func.count(Complaint.complaint_id)
    ).group_by(Complaint.status).all()

    #default counts
    status_data = {
        "total": 0,
        "submitted": 0,
        "in_progress": 0,
        "closed": 0
    }

    for status, count in complaint_counts:
        status_data["total"] += count
        if status == 'Submitted':
            status_data["submitted"] = count
        elif status == 'In Progress':
            status_data["in_progress"] = count
        elif status == 'Closed':
            status_data["closed"] = count

    return render_template("manage_complaints.html", current_user=current_user,
                           status_data=status_data,
                            complaint_status_html = complaint_status_html,
                            complaint_department_html = complaint_department_html)

#View complaints Route
@login_required
@admin.route('/complaint-centre/complaints')
def view_complaints():
    department = request.args.get('department')
    status = request.args.get('status')
    ##page
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = 3

    query = Complaint.query

    if department:
        query = query.filter_by(department=department)
    if status:
        query = query.filter_by(status=status)

    # pagination
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query = query.filter(Complaint.created_at.between(start_date, end_date))
        except ValueError:
            pass  # Ignore invalid date formats silently

    # complaints = query.order_by(Complaint.created_at.desc()).all()
    pagination = query.order_by(Complaint.created_at.desc()).paginate(page=page, per_page=per_page)
    complaints = pagination.items

    departments = [dept[0] for dept in db.session.query(Complaint.department.distinct()).all()]

    statuses = ['Submitted', 'In Progress', 'Closed']
    status_colors = {
        'Submitted': '#17a2b8',
        'Closed': '#28a745',
        'In Progress': '#ffc107'
    }
    return render_template('admin_complaints.html', complaints=complaints,
                           pagination=pagination,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           departments=departments, statuses=statuses, selected_department=department,
                           selected_status=status,status_colors=status_colors)

@login_required
@admin.route('/complaint-centre/complaints/<int:complaint_id>/update_status', methods=['POST'])
def update_complaint_status(complaint_id):
    new_status = request.form.get('status')
    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.status = new_status
    complaint.updated_at = datetime.now()
    db.session.commit()
    flash('Complaint status updated.', 'success')
    return redirect(url_for('admin.view_complaints'))

@login_required
@admin.route('/complaint-centre/complaints/<int:complaint_id>', methods=['GET', 'POST'])
def complaint_detail(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)

    if request.method == 'POST':
        admin_response = request.form.get('admin_response')

        complaint.admin_response = admin_response
        complaint.status =request.form.get('status') or complaint.status
        complaint.updated_at = datetime.now()


        response_entry = ComplaintResponse(
            complaint_id=complaint.complaint_id,
            user_email=current_user.email,
            response=admin_response,
            created_at=datetime.now()
        )
        db.session.add(response_entry)

        db.session.commit()
        flash('Response added successfully.', 'success')
        return redirect(url_for('admin.view_complaints', complaint_id=complaint_id))

    return render_template('admin_response_complaints.html', complaint=complaint)


## forget password
# @admin.route("/reset-password", methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated and current_user.user_detail:
#         print("yes")
#         return redirect(url_for('admin.a_dashboard'))
#
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         print(form.email.data)
#         admin = User.query.filter_by(email=form.email.data).first()
#         if admin:
#             print("no")
#             send_reset_email(admin)
#             flash('A password reset link has been sent to your email.', 'info')
#         else:
#             flash('No account found with that email.', 'warning')
#         return redirect(url_for('admin.login'))
#
#     return render_template('reset_request.html', form=form)
#
#
# @admin.route("/reset-password/<token>", methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated and current_user.user_detail:
#         return redirect(url_for('admin.a_dashboard'))
#
#     admin = User.verify_reset_token(token)
#     if admin is None:
#         flash('The reset link is invalid or has expired.', 'warning')
#         return redirect(url_for('admin.reset_request'))
#
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         admin.password = form.password.data
#         db.session.commit()
#         flash('Your password has been updated!', 'success')
#         return redirect(url_for('admin.login'))
#
#     return render_template('reset_token.html', form=form)


@admin.route('/analytics', methods=['GET'])
@login_required
def charts():
    users = User.query.all()
    tickets = FeedbackTicket.query.all()
    tasks = Task.query.all()
    complaints = Complaint.query.all()

    pio.templates.default = "plotly_white"

    chart_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='"Segoe UI", sans-serif', color='black', size=14),
        height=320,
        width=340,
        margin=dict(t=30, b=30, l=10, r=10),
        showlegend=True,
    )

    active_status_counts = Counter('Active' if u.is_active else 'Disabled' for u in users)
    active_status_chart = go.Figure(data=[go.Pie(
        labels=list(active_status_counts.keys()),
        values=list(active_status_counts.values()),
        marker=dict(colors=['#A8E6CF', '#FF8B94']),
        textinfo='percent+label',
        hole=0.3
    )])
    active_status_chart.update_layout(chart_layout)

    department_counts = Counter(u.department if u.department else 'No Department' for u in users)
    department_chart = go.Figure(data=[go.Bar(
        y=list(department_counts.keys()),
        x=list(department_counts.values()),
        orientation='h',
        name='User',
        marker_color='#AED6F1'
    )])
    department_chart.update_layout(chart_layout)

    role_counts = Counter(u.role for u in users)
    role_chart = go.Figure(data=[go.Scatter(
        x=list(role_counts.keys()),
        y=list(role_counts.values()),
        mode='lines+markers',
        name='Role',
        line=dict(color='#FF9F43', width=2),
        marker=dict(size=10)
    )])
    role_chart.update_layout(chart_layout)

    ticket_status_counts = Counter(t.ticket_status for t in tickets)
    ticket_chart = go.Figure(go.Sunburst(
        labels=list(ticket_status_counts.keys()),
        parents=[""] * len(ticket_status_counts),
        values=list(ticket_status_counts.values()),
        branchvalues="total",
        marker=dict(colors=['#A3E4D7', '#F9E79F', '#D5DBDB'])
    ))
    ticket_chart.update_layout(chart_layout)

    f_department_counts = Counter(t.department_name if t.department_name else "No Department" for t in tickets)
    f_department_chart = go.Figure(data=[go.Bar(
        y=list(f_department_counts.keys()),
        x=list(f_department_counts.values()),
        orientation='h',
        name='Ticket',
        marker_color='#A3E4D7'
    )])
    f_department_chart.update_layout(chart_layout)

    assigned_task_department_counts = Counter(
        t.ticket.department_name if t.assigned_to_email else "Unassigned"
        for t in tasks
    )
    assigned_task_department_chart = go.Figure(data=[go.Histogram(
        x=list(assigned_task_department_counts.elements()),
        name='Assigned',
        marker_color='#FFB347'
    )])
    assigned_task_department_chart.update_layout(chart_layout)

    complaint_status_counts = Counter(c.status for c in complaints)
    complaint_status_chart = go.Figure(go.Treemap(
        labels=list(complaint_status_counts.keys()),
        parents=[""] * len(complaint_status_counts),
        values=list(complaint_status_counts.values()),
        marker=dict(
            colors=['#FFF5E1', '#FFE2E2', '#FFCFCF']
        ),
        textinfo="label+value+percent entry"
    ))
    complaint_status_chart.update_layout(chart_layout,width=310)

    complaint_department_counts = Counter(c.department if c.department else "No Department" for c in complaints)
    complaint_department_chart = go.Figure(data=[go.Pie(
        labels=list(complaint_department_counts.keys()),
        values=list(complaint_department_counts.values()),
        marker=dict(colors=['#C9E9D2', '#F6E58D', '#FF8B94', '#D5DBDB']),
        textinfo='percent+label',
        hole=0.3
    )])
    complaint_department_chart.update_layout(chart_layout)

    active_status_html = pio.to_html(active_status_chart, full_html=False)
    department_html = pio.to_html(department_chart, full_html=False)
    role_html = pio.to_html(role_chart, full_html=False)
    ticket_chart_html = pio.to_html(ticket_chart, full_html=False)
    f_department_html = pio.to_html(f_department_chart, full_html=False)
    assigned_task_department_html = pio.to_html(assigned_task_department_chart, full_html=False)
    complaint_status_html = pio.to_html(complaint_status_chart, full_html=False)
    complaint_department_html = pio.to_html(complaint_department_chart, full_html=False)

    return render_template('dashboard.html', current_user=current_user,
                           active_status_html=active_status_html,
                           department_html=department_html,
                           role_html=role_html,
                           ticket_chart_html=ticket_chart_html,
                           f_department_html=f_department_html,
                           assigned_task_department_html=assigned_task_department_html,
                           complaint_status_html=complaint_status_html,
                           complaint_department_html=complaint_department_html)
