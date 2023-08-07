import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from db import db

class Access_token(db.Model):
    __tablename__ = "access_tokens"
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    user_mail = db.Column(db.String(254), ForeignKey("users.mail"), nullable=False)
    token = db.Column(db.Text,nullable=True)
    AES_key = db.Column(db.Text, nullable=True)

    user = relationship("User", back_populates="access_token")
