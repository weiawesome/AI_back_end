import uuid
from sqlalchemy import func, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db import db

PURE_TEXT="Pure Text"
class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    user_mail = db.Column(db.String(254), ForeignKey("users.mail"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now(),nullable=False)
    status=db.Column(Enum("PENDING","SUCCESS","FAILURE"), default="PENDING",nullable=False)
    type = db.Column(Enum("ASR","OCR"), nullable=False)
    resource=db.Column(db.String(254), nullable=False)

    result=db.Column(db.JSON, nullable=True)

    user = relationship("User", back_populates="files")

