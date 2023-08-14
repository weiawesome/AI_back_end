from sqlalchemy import Enum
from sqlalchemy.orm import relationship
from db import db

class User(db.Model):
    __tablename__ = "users"
    mail = db.Column(db.String(254), primary_key=True)
    password = db.Column(db.String(254), nullable=True)
    salt = db.Column(db.BINARY(16), nullable=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(Enum("male", "female", "other"),default="other", nullable=False)

    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    api_key = relationship("Api_key", back_populates="user",uselist=False, cascade="all, delete-orphan")
    access_token = relationship("Access_token", back_populates="user",uselist=False, cascade="all, delete-orphan")

