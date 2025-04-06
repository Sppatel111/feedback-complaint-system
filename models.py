from sqlalchemy import Integer, String, CheckConstraint, ForeignKeyConstraint,ForeignKey,Text,DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship,DeclarativeBase
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


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

    user_detail = relationship("Detail", back_populates="user_auth",uselist=False)
    feedbacks = relationship("FeedbackTicket", back_populates="user", cascade="all, delete")
    responses = relationship("FeedbackResponse", back_populates="user", cascade="all, delete")
    tasks = relationship("Task", back_populates="assigned_user", cascade="all, delete")

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
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    task_status: Mapped[str] = mapped_column(String, CheckConstraint("task_status IN ('todo', 'in_progress', 'in_review','completed')"), default='todo')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    ticket = relationship("FeedbackTicket", back_populates="tasks")
    assigned_user = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f'<Task {self.task_id} - {self.task_status}>'

