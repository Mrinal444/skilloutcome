import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class EmploymentStatus(str, enum.Enum):
    EMPLOYED = "EMPLOYED"
    RESIGNED = "RESIGNED"
    TERMINATED = "TERMINATED"


class EmploymentRecord(Base):
    __tablename__ = "employment_records"

    employment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trainee_id = Column(Integer, ForeignKey("trainees.trainee_id"), nullable=False, index=True)
    employer_id = Column(Integer, ForeignKey("employers.employer_id"), nullable=False, index=True)
    job_role = Column(String(200), nullable=False)
    salary = Column(Float, nullable=False)
    joining_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(Enum(EmploymentStatus), default=EmploymentStatus.EMPLOYED, index=True)

    trainee = relationship("Trainee", back_populates="employment_records")
    employer = relationship("Employer", backref="employment_records")
