from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Employer(Base):
    __tablename__ = "employers"

    employer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    location = Column(String(100))
    verification_status = Column(Boolean, default=False)
