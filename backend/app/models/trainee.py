import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class SkillLevel(str, enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class Trainee(Base):
    __tablename__ = "trainees"

    trainee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    education = Column(String(100))
    location = Column(String(100))
    experience = Column(Integer, default=0)

    # Relationships
    user = relationship("User", backref="trainee_profile")
    skills = relationship("TraineeSkill", back_populates="trainee", cascade="all, delete-orphan")
    enrollments = relationship("TrainingEnrollment", back_populates="trainee")
    employment_records = relationship("EmploymentRecord", back_populates="trainee")
    followups = relationship("FollowUp", back_populates="trainee")


class TraineeSkill(Base):
    """Many-to-many junction between Trainee and Skill with a proficiency level."""
    __tablename__ = "trainee_skills"
    __table_args__ = (
        UniqueConstraint("trainee_id", "skill_id", name="uq_trainee_skill"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    trainee_id = Column(Integer, ForeignKey("trainees.trainee_id"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"), nullable=False)
    level = Column(Enum(SkillLevel), default=SkillLevel.BEGINNER)

    trainee = relationship("Trainee", back_populates="skills")
    skill = relationship("Skill", backref="trainee_links")
