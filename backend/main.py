from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from .preprocess import extract_transactions
from .ocr import extract_text
from . import schema
from . import crud
from .database import SessionLocal, engine
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


schema.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "TransactIQ API is running!"}

@app.post("/upload/")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text(str(file_path))
    structured_data = extract_transactions(extracted_text)

    if not structured_data:
        raise HTTPException(status_code=400, detail="No transactions found.")

    statement = crud.create_statement(db, {
        "user_id": user_id,
        "statement_period_start": datetime(2025, 1, 1),
        "statement_period_end": datetime(2025, 1, 31),
        "issued_date": datetime.utcnow(),
        "file_path": str(file_path)
    })

    inserted_transactions = []
    for transaction in structured_data:
        transaction["statement_id"] = statement.id
        transaction["user_id"] = user_id
        stored_transaction = crud.create_transaction(db, transaction)
        if stored_transaction:
            inserted_transactions.append(stored_transaction)

   
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "message": "Transactions stored successfully!",
        "total_inserted": len(inserted_transactions),
        "statement_id": statement.id,
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email
        }
    }


# @app.get("/transactions/{statement_id}", response_model=List[dict])
# def get_transactions(statement_id: int, db: Session = Depends(get_db)):
#     transactions = crud.get_transactions_by_statement_id(db, statement_id)
#     if not transactions:
#         raise HTTPException(status_code=404, detail="No transactions found.")
#     return transactions

@app.get("/insights/statement/{statement_id}")
def get_insights_by_statement(statement_id: int, db: Session = Depends(get_db)):
    return crud.generate_insights_for_statement(db, statement_id)

