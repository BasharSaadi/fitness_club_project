from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import Base
import enum


class GoalType(enum.Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    BODY_FAT_REDUCTION = "body_fat_reduction"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    GENERAL_FITNESS = "general_fitness"


class GoalStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class FitnessGoal(Base):
    """
    FitnessGoal entity - represents a member's fitness goal.
    
    Attributes:
        goal_id: Primary key
        member_id: Foreign key to Member
        goal_type: Type of fitness goal
        target_value: Target value to achieve (e.g., target weight in kg)
        current_value: Current progress value
        deadline: Target date to achieve the goal
        status: Current status of the goal
        created_at: When the goal was created
    """
    __tablename__ = 'fitness_goals'

    goal_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False, index=True)
    goal_type = Column(Enum(GoalType), nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=True)
    deadline = Column(Date, nullable=True)
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("Member", back_populates="fitness_goals")

    def __repr__(self):
        return f"<FitnessGoal(id={self.goal_id}, type='{self.goal_type.value}', status='{self.status.value}')>"

    def to_dict(self):
        """Convert fitness goal to dictionary representation."""
        return {
            'goal_id': self.goal_id,
            'member_id': self.member_id,
            'goal_type': self.goal_type.value,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'deadline': str(self.deadline) if self.deadline else None,
            'status': self.status.value,
            'created_at': str(self.created_at)
        }

    def progress_percentage(self):
        """Calculate progress towards the goal as a percentage."""
        if self.current_value is None or self.target_value == 0:
            return 0
        
        if self.goal_type in [GoalType.WEIGHT_LOSS, GoalType.BODY_FAT_REDUCTION]:
            # For reduction goals, lower is better
            initial = self.current_value  # Assuming current_value starts at initial
            if self.target_value >= initial:
                return 100  # Already at or below target
            return min(100, max(0, ((initial - self.current_value) / (initial - self.target_value)) * 100))
        else:
            # For gain/increase goals, higher is better
            return min(100, (self.current_value / self.target_value) * 100)
