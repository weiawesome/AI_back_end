import uuid
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import relationship
from db import db

class Api_key(db.Model):
    __tablename__ = "api_keys"
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    user_mail = db.Column(db.String(254), ForeignKey("users.mail"), nullable=False)
    key = db.Column(db.Text,nullable=True)
    AES_key = db.Column(db.Text, nullable=True)

    user = relationship("User", back_populates="api_key")
