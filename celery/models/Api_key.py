import uuid

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import relationship

from db import db

class Api_key(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.BINARY(16), primary_key=True, default=uuid.uuid4().bytes, unique=True, nullable=False)
    mail = db.Column(db.String(254),ForeignKey('users.mail'),nullable=False)
    key = db.Column(db.Text,nullable=True)
    AES_key = db.Column(db.Text, nullable=True)

    user = relationship("User", back_populates="api_key")

    def __repr__(self):
        return '<User %r>' % self.mail
