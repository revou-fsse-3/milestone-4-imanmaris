
from app.models.base import Base
from sqlalchemy import Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import func
from app.models.accounts import Account

class Transaction(Base):
    __tablename__ = "transactions"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_account_id = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"))
    to_account_id = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"))
    amount = mapped_column(DECIMAL(precision=10, scale=2))
    type = mapped_column(String(255), nullable= False)
    description = mapped_column(String(255), nullable= False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship list
    accounts = relationship("Account", cascade="all,delete-orphan")

    def __repr__(self):
        return f'<Transaction {self.type}>'