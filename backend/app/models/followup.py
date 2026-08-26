import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


class FollowUpType(str, enum.Enum):
    DAY_30 = "DAY_30"
    DAY_90 = "DAY_90"
    DAY_180 = "DAY_180"


class FollowUpStatus(str, enum.Enum):
    EMPLOYED = "EMPLOYED"
    UNEMPLOYED = "UNEMPLOYED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    FURTHER_TRAINING = "FURTHER_TRAINING"


class FollowUp(Base):
    __tablename__ = "followups"

    followup_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trainee_id = Column(Integer, ForeignKey("trainees.trainee_id"), nullable=False, index=True)
    follow_up_type = Column(Enum(FollowUpType), nullable=False, index=True)
    status = Column(Enum(FollowUpStatus), nullable=False)
    salary = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trainee = relationship("Trainee", back_populates="followups")
