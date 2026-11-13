
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    String, Integer, ForeignKey, Date, Numeric, DateTime, Text
)
from sqlalchemy.orm import Mapped, mapped_column

from db.session import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    legacy_customer_id: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    legacy_vendor_id: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    legacy_invoice_id: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True
    )
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), nullable=False
    )
    vendor_id: Mapped[int] = mapped_column(
        ForeignKey("vendors.id"), nullable=False
    )

    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)


class InvoiceStaging(Base):
    __tablename__ = "invoice_staging"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    legacy_invoice_id: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=True)
    customer_legacy_id: Mapped[str] = mapped_column(String(50), nullable=True)
    vendor_legacy_id: Mapped[str] = mapped_column(String(50), nullable=True)
    invoice_date_raw: Mapped[str] = mapped_column(String(50), nullable=True)
    amount_raw: Mapped[str] = mapped_column(String(50), nullable=True)
    currency_raw: Mapped[str] = mapped_column(String(10), nullable=True)


class MigrationException(Base):
    __tablename__ = "migration_exceptions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    entity: Mapped[str] = mapped_column(String(20), nullable=False)
    record_id: Mapped[str] = mapped_column(String(50), nullable=False)
    rule_id: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    original_value: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    corrected_value: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
