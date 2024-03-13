from app.models.base import Base
from sqlalchemy import Integer, String, Text, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func


class Account(Base):
    __tablename__ = 'accounts'

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    account_type = mapped_column(String(255), nullable= False)
    account_number = mapped_column(String(255), nullable= False, unique=True)
    balance = mapped_column(DECIMAL(precision=10, scale=2))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f'<Account {self.id}>'