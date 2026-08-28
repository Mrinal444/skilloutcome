import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float, Index
from sqlalchemy.orm import relationship
from app.database import Base


class EnrollmentStatus(str, enum.Enum):
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    DROPPED = "DROPPED"


class TrainingProgram(Base):
    __tablename__ = "training_programs"

    program_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    provider = Column(String(200), nullable=False)
    duration = Column(String(50))
    category = Column(String(100))
    provider_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    enrollments = relationship("TrainingEnrollment", back_populates="program")


class TrainingEnrollment(Base):
    __tablename__ = "training_enrollments"

    enrollment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trainee_id = Column(Integer, ForeignKey("trainees.trainee_id"), nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("training_programs.program_id"), nullable=False, index=True)
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completion_date = Column(DateTime, nullable=True)
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ONGOING, index=True)
    score = Column(Float, nullable=True)

    trainee = relationship("Trainee", back_populates="enrollments")
    program = relationship("TrainingProgram", back_populates="enrollments")
