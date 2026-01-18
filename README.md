# Employee Interaction Management System (EIMS)

[![License: Creative Commons](https://img.shields.io/badge/License-CC_BY--NC_4.0-blue.svg)](https://creativecommons.org/licenses/by-nc/4.0/deed.en)

## Description

The **Employee Interaction Management System** is a Flask-based web application that manages employee feedback, complaints, and related tasks. It provides role-based dashboards for **Admins** and **Employees** to ensure streamlined workflows, from complaint submission to task assignment and resolution.

### **Key Highlights**
- **UUID-based unique filenames** for profile images.
- Secure password storage using **Werkzeug.security**.
- **PostgreSQL** database with **SQLAlchemy ORM**.
- Email notifications via **Flask-Mail** and **smtplib**.
- Analytics dashboard using **Plotly** for complaint and feedback trends.
- Environment variable management using **python-dotenv**.

---

## Key Features

### **User Features**
- Submit feedback and complaints with file attachments.
- Track complaint status (**Submitted**, **In Progress**, **Closed**).
- View complaint history and admin responses.
- Access and update **assigned tasks** with status changes.
- Manage profile details and upload profile images (UUID-based filenames).

### **Admin Features**
- View and manage all complaints and feedback tickets.
- Respond to complaints and feedback.
- Assign tasks with deadlines and priorities.
- Generate **visual reports** using Plotly.
- Manage users (Add, Activate/Deactivate).

### **Filters and Search**
- Filter by **department**, **status**, and **date range**.
- Search complaints or feedback by **ID** or **title**.

---

## System Workflow
1. Users submit feedback or complaints.
2. Admin reviews submissions, responds, and assigns tasks if required.
3. Users update task status; admins track progress.
4. Admin views dashboards and generates insights via Plotly.

---

## Tech Stack
- **Backend:** Flask, Flask-WTF, Flask-Login
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Migrations:** Flask-Migrate (Alembic)
- **Frontend:** HTML5, CSS3 (Bootswatch Lux), JavaScript
- **Security:** Password hashing using Werkzeug
- **Analytics:** Plotly
- **Email Service:** Flask-Mail & smtplib
- **Environment Management:** python-dotenv
- **Python Version:** 3.x

---
### 🎞️ Project Demo (GIF Preview)

![App Demo](demo/demo.gif)

[Download Demo Video](demo/FeedbackSystemDemo.mp4)


---

## Database Schema

### **1. user_auth**
| Column       | Type     | Constraints |
|-------------|---------|------------|
| email       | String  | Primary Key, Unique, Not Null |
| password    | String  | Not Null |
| department  | String  | Check: ('AI/ML', 'Python', 'QA', 'UI/UX', 'Frontend') |
| role        | String  | Check: ('admin', 'employee'), Not Null |
| is_active   | Boolean | Default: True |
| created_at  | DateTime| Default: current timestamp |

**Relationships:**  
- One-to-One → `user_detail`  
- One-to-Many → `feedback_tickets`, `feedback_responses`, `tasks`, `complaints`

---

### **2. user_detail**
| Column       | Type     | Constraints |
|-------------|---------|------------|
| email       | String  | Primary Key, Foreign Key → user_auth.email (CASCADE) |
| firstname   | String  | Nullable |
| lastname    | String  | Nullable |
| phone_number| String  | Nullable |
| profile_image| String | Default: 'default-profile.jpg' |

---

### **3. feedback_tickets**
| Column         | Type     | Constraints |
|---------------|---------|------------|
| ticket_id     | Integer | Primary Key, Auto Increment |
| user_email    | String  | FK → user_auth.email (CASCADE) |
| department_name| String | Not Null |
| ticket_label  | String  | Not Null |
| question      | Text    | Not Null |
| created_at    | DateTime| Default: current timestamp |
| ticket_status | String  | Check: ('open', 'closed', 'in_progress'), Default: 'open' |

**Relationships:**  
- One-to-Many → `feedback_responses`, `tasks`

---

### **4. feedback_responses**
| Column       | Type     | Constraints |
|-------------|---------|------------|
| response_id | Integer | Primary Key, Auto Increment |
| ticket_id   | Integer | FK → feedback_tickets.ticket_id (CASCADE) |
| user_email  | String  | FK → user_auth.email (SET NULL) |
| response    | Text    | Not Null |
| created_at  | DateTime| Default: current timestamp |

---

### **5. tasks**
| Column       | Type     | Constraints |
|-------------|---------|------------|
| task_id     | Integer | Primary Key, Auto Increment |
| ticket_id   | Integer | FK → feedback_tickets.ticket_id (CASCADE) |
| assigned_to_email| String| FK → user_auth.email (SET NULL) |
| details     | Text    | Not Null |
| deadline    | DateTime| Not Null |
| task_status | String  | Check: ('todo','in_progress','backlog','in_review','done','completed'), Default: 'todo' |
| priority    | String  | Check: ('low','medium','high'), Default: 'medium' |
| created_at  | DateTime| Default: current timestamp |

---

### **6. complaints**
| Column       | Type     | Constraints |
|-------------|---------|------------|
| complaint_id| Integer | Primary Key, Auto Increment |
| user_email  | String  | FK → user_auth.email (CASCADE) |
| title       | String(100)| Not Null |
| department  | String(50)| Not Null |
| description | Text    | Not Null |
| attachment  | String(255)| Nullable |
| status      | String(20)| Check: ('Submitted','In Progress','Closed'), Default: 'Submitted' |
| admin_response| Text  | Nullable |
| created_at  | DateTime| Default: current timestamp |
| updated_at  | DateTime| On Update current timestamp |

**Relationships:**  
- One-to-Many → `complaint_responses`

---

### **7. complaint_responses**
| Column       | Type     | Constraints |
|-------------|---------|------------|
| id          | Integer | Primary Key, Auto Increment |
| complaint_id| Integer | FK → complaints.complaint_id (CASCADE) |
| user_email  | String  | Not Null |
| response    | Text    | Not Null |
| created_at  | DateTime| Default: current timestamp |

---

## System Flow Diagram
*(Add `/static/system_flow.png` here)*

---

## Usage

### **1. Clone repository**
```bash
git clone https://github.com/your-username/feedback-complaint-management.git
```
### 2. Create Virtual Environment

#### Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

Make sure `pip` is up to date, then install all required packages using:

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root directory and add the following:

```ini
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/feedback_system

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_USE_TLS=True
```

> ⚠️ Replace placeholders with your actual credentials and configuration.

---

### 5. Set Up Database

Initialize and apply database migrations using Flask-Migrate:

```bash
flask db init
flask db migrate
flask db upgrade
```

---

### 6. Run the Application

Start the development server:

```bash
python app.py
```

Once started, visit the app in your browser:

```
http://localhost:5000
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---


