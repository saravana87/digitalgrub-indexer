"""
Database models for DigitalGrub Indexer
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

Base = declarative_base()


class Job(Base):
    """Jobs table model"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    link = Column(Text)
    company = Column(String(500))
    company_link = Column(Text)
    role = Column(String(500))
    open_until = Column(String(200))
    salary = Column(String(200))
    location = Column(String(500))
    sector = Column(String(500))
    sector_link = Column(Text)
    openings = Column(String(100))
    image = Column(Text)
    apply_link = Column(Text)
    job_type = Column(String(200))
    start_date = Column(Date)
    end_date = Column(Date)
    description = Column(Text)
    skills = Column(Text)
    experience = Column(String(200))
    education = Column(String(500))
    age_limit = Column(String(100))
    gender = Column(String(50))
    marital_status = Column(String(50))
    work_location = Column(String(500))
    work_shift = Column(String(200))
    applications_from = Column(String(500))
    company_address = Column(Text)
    urgently_hiring = Column(Boolean)
    site_source = Column(String(200))
    index_status = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_document_text(self) -> str:
        """Convert job record to text for indexing"""
        parts = []
        
        if self.title:
            parts.append(f"Job Title: {self.title}")
        if self.company:
            parts.append(f"Company: {self.company}")
        if self.role:
            parts.append(f"Role: {self.role}")
        if self.location:
            parts.append(f"Location: {self.location}")
        if self.sector:
            parts.append(f"Sector: {self.sector}")
        if self.salary:
            parts.append(f"Salary: {self.salary}")
        if self.experience:
            parts.append(f"Experience Required: {self.experience}")
        if self.education:
            parts.append(f"Education: {self.education}")
        if self.job_type:
            parts.append(f"Job Type: {self.job_type}")
        if self.description:
            parts.append(f"Description: {self.description}")
        if self.skills:
            parts.append(f"Skills Required: {self.skills}")
        
        return "\n".join(parts)
    
    def to_metadata(self) -> dict:
        """Extract metadata for filtering"""
        return {
            "id": self.id,
            "company": self.company or "",
            "location": self.location or "",
            "sector": self.sector or "",
            "job_type": self.job_type or "",
            "salary": self.salary or "",
            "experience": self.experience or "",
            "site_source": self.site_source or "",
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }


class TNNews(Base):
    """TN News table model - adjust columns based on your actual schema"""
    __tablename__ = 'tnnews'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    link = Column(Text)
    content = Column(Text)
    category = Column(String(200))
    published_date = Column(DateTime)
    source = Column(String(200))
    index_status = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_document_text(self) -> str:
        """Convert news record to text for indexing"""
        parts = []
        
        if self.title:
            parts.append(f"Title: {self.title}")
        if self.category:
            parts.append(f"Category: {self.category}")
        if self.content:
            parts.append(f"Content: {self.content}")
        if self.source:
            parts.append(f"Source: {self.source}")
        
        return "\n".join(parts)
    
    def to_metadata(self) -> dict:
        """Extract metadata for filtering"""
        return {
            "id": self.id,
            "category": self.category or "",
            "source": self.source or "",
            "published_date": self.published_date.isoformat() if self.published_date else "",
        }


class AIJob(Base):
    """AI Jobs table model - adjust columns based on your actual schema"""
    __tablename__ = 'aijobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    link = Column(Text)
    company = Column(String(500))
    location = Column(String(500))
    description = Column(Text)
    skills = Column(Text)
    experience = Column(String(200))
    salary = Column(String(200))
    job_type = Column(String(200))
    index_status = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_document_text(self) -> str:
        """Convert AI job record to text for indexing"""
        parts = []
        
        if self.title:
            parts.append(f"Job Title: {self.title}")
        if self.company:
            parts.append(f"Company: {self.company}")
        if self.location:
            parts.append(f"Location: {self.location}")
        if self.description:
            parts.append(f"Description: {self.description}")
        if self.skills:
            parts.append(f"Skills: {self.skills}")
        if self.experience:
            parts.append(f"Experience: {self.experience}")
        if self.salary:
            parts.append(f"Salary: {self.salary}")
        
        return "\n".join(parts)
    
    def to_metadata(self) -> dict:
        """Extract metadata for filtering"""
        return {
            "id": self.id,
            "company": self.company or "",
            "location": self.location or "",
            "job_type": self.job_type or "",
            "experience": self.experience or "",
        }


# Database engine and session
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
