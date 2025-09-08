from typing import List
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import Category, File, Cell


class CategoryRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get(self, category_name: str) -> Category:
        return self.db_session.query(Category).filter_by(name=category_name).first()

    def create(self, category_name: str, region: str, type: str) -> Category:
        category = Category(
            name=category_name,
            region=region,
            type=type,
        )
        self.db_session.add(category)
        self.db_session.flush()  # required to update id on object
        return category

    def sum_type(self, _type: str) -> float:
        stmt = (
            select(func.sum(Cell.float_value))
            .join(File, Cell.file_id == File.id)
            .join(Category, File.category_id == Category.id)
            .where(Category.type == _type)
            .where(
                Cell.float_value.is_not(None)
            )  # to skip cells with string value
        )
        total = self.db_session.execute(stmt).scalar()
        return float(total) if total is not None else 0.0

    def find_regions(self, search_term: str) -> List[str]:
        term = f"%{search_term}%"

        stmt = (
            select(Category.region)
            .distinct()
            .join(File, File.category_id == Category.id)
            .join(Cell, Cell.file_id == File.id)
            .where(Cell.str_value.ilike(term))
        )

        return self.db_session.execute(stmt).scalars().all()


class FileRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, category_id: int, name: str, contents: bytes) -> File:
        file = File(
            category_id=category_id,
            name=name,
            binary_data=contents,
        )
        self.db_session.add(file)
        self.db_session.flush()  # required to update id on object
        return file


class CellRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(
        self, file_id: int, str_value: str = None, float_value: float = None
    ) -> Cell:
        cell = Cell(
            file_id=file_id,
            str_value=str_value,
            float_value=float_value,
        )
        self.db_session.add(cell)
        return cell
