import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import relationship

from domain.entities.product import ProductStatus
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
    status = Column(
        SAEnum(ProductStatus, values_callable=lambda e: [v.value for v in e]),
        nullable=False,
        default=ProductStatus.PROCESSING,
    )
    image_urls = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    category = relationship("CategoryModel", back_populates="products", lazy="select")
    skus = relationship("SkuModel", back_populates="product", lazy="select", cascade="all, delete-orphan")


class SkuModel(Base):
    __tablename__ = "skus"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    attributes = Column(JSON, nullable=False, default=dict)
    # None means "inherit the parent product's price"
    price_amount = Column(Numeric(10, 2), nullable=True)
    price_currency = Column(String(3), nullable=True)
    stock = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    product = relationship("ProductModel", back_populates="skus", lazy="select")


__all__ = ["CategoryModel", "ProductModel", "SkuModel"]
