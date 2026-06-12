from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.enums import InspectionResultEnum


class Inspection(db.Model):
    __tablename__ = "inspection"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    batch_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    serial_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    inspection_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    result: Mapped[InspectionResultEnum] = mapped_column(
        Enum(
            InspectionResultEnum,
            name="inspection_result",
            native_enum=True,
        ),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("product.id"),
        nullable=False,
    )

    inspector_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("inspector.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    product = relationship(
        "Product",
        back_populates="inspections",
    )

    inspector = relationship(
        "Inspector",
        back_populates="inspections",
    )

    defects = relationship(
        "Defect",
        back_populates="inspection",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"Inspection batch={self.batch_number} result={self.result.value}"