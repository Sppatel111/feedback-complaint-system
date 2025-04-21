from sqlalchemy import Integer, String, CheckConstraint, ForeignKeyConstraint, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship, DeclarativeBase
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import List


# create database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(UserMixin, db.Model):
    __tablename__ = 'user_auth'
    email: Mapped[str] = mapped_column(String, primary_key=True, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str] = mapped_column(String,
        CheckConstraint("department IN('AI/ML', 'Python', 'QA', 'UI/UX', 'Frontend') OR department IS NULL"),
        nullable=True)
    role: Mapped[str] = mapped_column(String, CheckConstraint("role IN ('admin', 'employee')"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    user_detail = relationship("Detail", back_populates="user_auth",uselist=False)
    feedbacks = relationship("FeedbackTicket", back_populates="user", cascade="all, delete")
    responses = relationship("FeedbackResponse", back_populates="user", cascade="all, delete")
    tasks = relationship("Task", back_populates="assigned_user", cascade="all, delete")
    complaints = relationship("Complaint", back_populates="user",cascade="all, delete")
    # complaint_response=relationship("ComplaintResponse",back_populates="user",cascade="all, delete")

    def __repr__(self):
        return f'<User {self.email}>'

    def get_id(self):
        return self.email

class Detail(db.Model):
    __tablename__ = 'user_detail'
    email: Mapped[str] = mapped_column(String, primary_key=True)
    firstname: Mapped[str] = mapped_column(String, nullable=True)
    lastname: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    profile_image: Mapped[str] = mapped_column(String, default=('default-profile.jpg'), nullable=True)
    __table_args__ = (ForeignKeyConstraint
                      (['email'], ['user_auth.email'], ondelete='CASCADE'),
                      )

    user_auth = relationship("User", back_populates="user_detail")

    def __repr__(self):
        return f'<Detail {self.email}>'

# Feedback Ticket Model
class FeedbackTicket(db.Model):
    __tablename__ = 'feedback_tickets'

    ticket_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_email: Mapped[str] = mapped_column(String, ForeignKey('user_auth.email', ondelete="CASCADE"), nullable=False)
    department_name: Mapped[str] = mapped_column(String, nullable=False)
    ticket_label: Mapped[str] = mapped_column(String,nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    ticket_status: Mapped[str] = mapped_column(String, CheckConstraint("ticket_status IN ('open', 'closed', 'in_progress')"), default='open')

    user = relationship("User", back_populates="feedbacks")
    responses = relationship("FeedbackResponse", back_populates="ticket", cascade="all, delete")
    tasks = relationship("Task", back_populates="ticket", cascade="all, delete")

    def __repr__(self):
        return f'<FeedbackTicket {self.ticket_id} - {self.ticket_status}>'

# Feedback Response Model
class FeedbackResponse(db.Model):
    __tablename__ = 'feedback_responses'

    response_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey('feedback_tickets.ticket_id', ondelete="CASCADE"), nullable=False)
    user_email: Mapped[str] = mapped_column(String, ForeignKey('user_auth.email', ondelete="SET NULL"), nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    ticket = relationship("FeedbackTicket", back_populates="responses")
    user = relationship("User", back_populates="responses")

    def __repr__(self):
        return f'<FeedbackResponse {self.response_id}>'

# Task Model
class Task(db.Model):
    __tablename__ = 'tasks'

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey('feedback_tickets.ticket_id', ondelete="CASCADE"), nullable=False)
    assigned_to_email: Mapped[str] = mapped_column(String, ForeignKey('user_auth.email', ondelete="SET NULL"), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    task_status: Mapped[str] = mapped_column(String, CheckConstraint("task_status IN ('todo', 'in_progress','backlog','in_review','done','completed')"), default='todo')
    priority: Mapped[str] = mapped_column(String, CheckConstraint("priority IN ('low', 'medium', 'high')"),default='medium')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    ticket = relationship("FeedbackTicket", back_populates="tasks")
    assigned_user = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f'<Task {self.task_id} - {self.task_status}>'

# Complaint Model
class Complaint(db.Model):
    __tablename__ = 'complaints'

    complaint_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_email: Mapped[str] = mapped_column(String, ForeignKey('user_auth.email', ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    attachment: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('Submitted', 'In Progress', 'Closed')"),
        default='Submitted',
        nullable=False
    )
    admin_response: Mapped[str] = mapped_column(Text, nullable=True)
    # notification: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.now(), nullable=True)

    responses: Mapped[List["ComplaintResponse"]] = relationship("ComplaintResponse", back_populates="complaint",
                                                                cascade="all, delete-orphan")
    user = relationship("User", back_populates="complaints")

    def __repr__(self):
        return f"<Complaint {self.complaint_id} - {self.status}>"


class ComplaintResponse(db.Model):
    __tablename__ = 'complaint_responses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(Integer, ForeignKey('complaints.complaint_id', ondelete="CASCADE"), nullable=False)
    user_email: Mapped[str] = mapped_column(String, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    complaint = relationship("Complaint", back_populates="responses")

    def __repr__(self):
        return f"<Response #{self.id} by {self.user_email} on complaint {self.complaint_id}>"