import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from infrastructure.persistence.database import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    products = relationship("ProductModel", back_populates="category", lazy="select")


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, default="", nullable=False)
    price_amount = Column(Numeric(10, 2), nullable=False)
    price_currency = Column(String(3), default="USD", nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    category_id = Column(String, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    category = relationship("CategoryModel", back_populates="products", lazy="select")


__all__ = ["CategoryModel", "ProductModel"]
