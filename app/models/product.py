from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Product(db.Model):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    product_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    product_family: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    revision: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    inspections = relationship(
        "Inspection",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    defects = relationship(
        "Defect",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"Product code={self.product_code}"