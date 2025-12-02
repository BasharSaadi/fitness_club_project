from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class HealthMetric(Base):
    """
    HealthMetric entity - represents a health measurement entry.
    
    These entries are append-only (never overwritten) to maintain
    a complete history of member health data over time.
    
    Attributes:
        metric_id: Primary key
        member_id: Foreign key to Member
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        heart_rate_bpm: Resting heart rate in beats per minute
        body_fat_percentage: Body fat percentage
        recorded_at: Timestamp when measurement was recorded
    """
    __tablename__ = 'health_metrics'

    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False, index=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    heart_rate_bpm = Column(Integer, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    member = relationship("Member", back_populates="health_metrics")

    def __repr__(self):
        return f"<HealthMetric(id={self.metric_id}, member_id={self.member_id}, recorded_at='{self.recorded_at}')>"

    def to_dict(self):
        """Convert health metric to dictionary representation."""
        return {
            'metric_id': self.metric_id,
            'member_id': self.member_id,
            'weight_kg': self.weight_kg,
            'height_cm': self.height_cm,
            'heart_rate_bpm': self.heart_rate_bpm,
            'body_fat_percentage': self.body_fat_percentage,
            'recorded_at': str(self.recorded_at)
        }
