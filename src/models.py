from __future__ import annotations

from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    LargeBinary,
    String,
    Float,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import text


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    region: Mapped[str] = mapped_column(String(256), nullable=False)
    type: Mapped[str] = mapped_column(String(256), nullable=False)
    files: Mapped[List["File"]] = relationship(
        back_populates="category", cascade="all, delete-orphan" #TODO do we need it?
    )

    __table_args__ = (
        Index("idx_categories_type", "type"),
        Index("idx_categories_name", "name"),
    )


class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    binary_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    category: Mapped["Category"] = relationship(back_populates="files")
    cells: Mapped[List["Cell"]] = relationship(
        back_populates="file", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_files_category_id", "category_id"),
    )


class Cell(Base):
    __tablename__ = "cells"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"), nullable=False
    )
    str_value: Mapped[Optional[str]] = mapped_column(String(32767))
    float_value: Mapped[Optional[float]] = mapped_column(Float)
    file: Mapped["File"] = relationship(back_populates="cells")
    __table_args__ = (
        CheckConstraint(
            "(str_value IS NOT NULL OR float_value IS NOT NULL)",
            name="cells_value_not_null",
        ),
        Index("idx_cells_file_id", "file_id"),
        Index("idx_cells_float_value", "float_value"),
        # GIN trigram index for fast ILIKE '%term%' on str_value TODO change to better comment
        # Equivalent to: CREATE INDEX idx_cells_str_trgm ON cells USING GIN (str_value gin_trgm_ops);
        Index(
            "idx_cells_str_trgm",
            text("str_value gin_trgm_ops"),
            postgresql_using="gin",
        ),
    )
