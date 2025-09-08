from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from io import BytesIO
import numpy as np
import pandas as pd
from typing import Annotated
from sqlalchemy.orm import Session
from src.db import get_session
from fastapi import Depends
from pydantic import Field

from src.repository import CategoryRepository, FileRepository, CellRepository


app = FastAPI(title="FastAPI Excel Parser")

DBSessionDep = Annotated[Session, Depends(get_session)]
Str256 = Annotated[str, Field(min_length=1, max_length=256)]


def error_response(error_text: str) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": error_text})


@app.post("/create_category")
async def create_category(
    category_name: Str256, region: Str256, type: Str256, db_session: DBSessionDep
):
    category_repo = CategoryRepository(db_session)
    if category_repo.get(category_name):
        return error_response(f"Category {category_name} exists")
    category = category_repo.create(category_name, region, type)
    return {
        "id": category.id,
        "name": category.name,
        "region": category.region,
        "type": category.type,
    }


@app.post("/upload_file")
async def upload_excel(
    category_name: Str256, file: UploadFile, db_session: DBSessionDep
):
    if file.content_type not in (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ):
        return error_response(
            f"Please upload an Excel file (.xlsx/.xls), not {file.content_type}"
        )

    category_repo = CategoryRepository(db_session)
    category = category_repo.get(category_name)
    if not category:
        return error_response(f"Category {category_name} exists")

    contents = await file.read()
    if not contents:
        return error_response("Empty file")

    try:
        xls = pd.ExcelFile(BytesIO(contents))
    except Exception as e:
        return error_response(f"Exception when parsing file: {e}")

    file_repo = FileRepository(db_session)
    db_file = file_repo.create(category.id, file.filename or "upload.xlsx", contents)
    processed_sheets = []
    float_values = 0
    str_values = 0
    other_values = 0
    for sheet in xls.sheet_names:
        processed_sheets.append(sheet)
        df = xls.parse(sheet, dtype=object)
        if df.size == 0:
            continue

        cell_repo = CellRepository(db_session)

        for _, row in df.iterrows():
            for col in df.columns:
                val = row[col]
                if pd.isna(val): # required to avoid saving NaN in numbers in DB
                    continue
                if isinstance(val, str) and val.strip() == "": # required to avoid saving empty or whitespace-only values in DB
                    continue
                if isinstance(val, (int, float, np.integer, np.floating)):
                    cell_repo.create(file_id=db_file.id, float_value=val)
                    float_values += 1
                elif isinstance(val, str):
                    cell_repo.create(file_id=db_file.id, str_value=val)
                    str_values += 1
                else:
                    print(f"TODO !!! non-number, non-string value {val}")
                    other_values += 1

    return {
        "filename": file.filename,
        "sheets": processed_sheets,
        "float_values": float_values,
        "str_values": str_values,
    }


@app.get("/sum_type")
def sum_type(type: Str256, db_session: DBSessionDep):
    category_repo = CategoryRepository(db_session)
    sum = category_repo.sum_type(type)
    return {
        "sum": sum
    }


@app.get("/find_regions")
def find_regions(search_term: Str256, db_session: DBSessionDep):
    category_repo = CategoryRepository(db_session)
    regions = category_repo.find_regions(search_term)
    return {
        "regions": regions
    }
