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

