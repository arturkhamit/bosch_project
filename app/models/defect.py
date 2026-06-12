from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.enums import DefectSeverityEnum, DefectStatusEnum


class Defect(db.Model):
    __tablename__ = "defect"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    defect_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    defect_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    severity: Mapped[DefectSeverityEnum] = mapped_column(
        Enum(
            DefectSeverityEnum,
            name="defect_severity",
            native_enum=True,
        ),
        nullable=False,
    )

    status: Mapped[DefectStatusEnum] = mapped_column(
        Enum(
            DefectStatusEnum,
            name="defect_status",
            native_enum=True,
        ),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    root_cause: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    corrective_action: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("product.id"),
        nullable=False,
    )

    inspection_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("inspection.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    product = relationship(
        "Product",
        back_populates="defects",
    )

    inspection = relationship(
        "Inspection",
        back_populates="defects",
    )

    def __repr__(self):
        return f"Defect code={self.defect_code} status={self.status.value}"