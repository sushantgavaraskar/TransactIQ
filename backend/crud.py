import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend import schema
from backend.preprocess import categorize_transaction
from backend.schema import Transaction
from collections import defaultdict
from typing import Dict, Any
from datetime import datetime

# ✅ Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ✅ Create Statement
def create_statement(db: Session, statement_data: dict):
    try:
        statement = schema.Statement(**statement_data)
        db.add(statement)
        db.commit()
        db.refresh(statement)
        logger.info(f"✅ Statement ID {statement.id} created for User {statement.user_id}")
        return statement
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating statement: {str(e)}")
        return None

# ✅ Assign Category using BERT Model
def get_category(description: str):
    """Uses the BERT model to classify transaction descriptions."""
    return categorize_transaction(description)

# ✅ Create Transaction (with Category Assignment)
# def create_transaction(db: Session, transaction_data: dict):
#     try:
#         description = transaction_data.get("description", "").strip()
#         transaction_data["category"] = get_category(description)

#         transaction = models.Transaction(**transaction_data)
#         db.add(transaction)
#         db.commit()
#         db.refresh(transaction)
#         logger.info(f"✅ Transaction {transaction.id} stored under Statement {transaction.statement_id}")
#         return transaction
#     except Exception as e:
#         db.rollback()
#         logger.error(f"❌ Error storing transaction: {str(e)}")
#         return None

def create_transaction(db: Session, transaction_data: dict):
    try:
        description = transaction_data.get("description", "").strip()

        # Assign category if missing
        transaction_data["category"] = get_category(description)

        # Heuristic for transaction type (optional fallback)
        if "transaction_type" not in transaction_data or not transaction_data["transaction_type"]:
            if transaction_data.get("amount", 0) < 0:
                transaction_data["transaction_type"] = "debit"
                transaction_data["amount"] = abs(transaction_data["amount"])
            else:
                transaction_data["transaction_type"] = "credit"

        # Extract merchant name (very basic logic)
        if not transaction_data.get("merchant_name"):
            transaction_data["merchant_name"] = description.split()[0] if description else "Unknown"

        transaction = schema.Transaction(**transaction_data)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        logger.info(f"✅ Transaction {transaction.id} stored under Statement {transaction.statement_id}")
        return transaction

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error storing transaction: {str(e)}")
        return None


def generate_insights_for_statement(db: Session, statement_id: int) -> Dict[str, Any]:
    transactions = db.query(Transaction).filter(Transaction.statement_id == statement_id).all()
    if not transactions:
        return {
            "expense_breakdown": {},
            "monthly_spending": {},
            "income_vs_expenses": {"income": {}, "expenses": {}},
            "high_value_transactions": [],
            "recurring_transactions": {},
            "top_merchants": {}
        }

    expense_breakdown = defaultdict(float)
    monthly_spending = defaultdict(float)
    income_by_month = defaultdict(float)
    expenses_by_month = defaultdict(float)
    merchant_totals = defaultdict(float)
    recurring_check = defaultdict(list)
    high_value_threshold = 50000  # Customize as needed
    high_value_transactions = []

    for txn in transactions:
        date_obj = txn.transaction_date
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        month_key = date_obj.strftime("%Y-%m")

        amount = txn.amount or 0.0
        merchant = txn.merchant_name or "Unknown"
        category = txn.category or "Uncategorized"
        description = txn.description or ""

        # Classify as income or expense
        if txn.transaction_type and txn.transaction_type.lower() == "credit":
            if "salary" in description.lower() or "income" in description.lower() or "employer" in description.lower():
                income_by_month[month_key] += amount
            else:
                expenses_by_month[month_key] += amount
                expense_breakdown[category] += amount
                monthly_spending[month_key] += amount
        else:
            expenses_by_month[month_key] += amount
            expense_breakdown[category] += amount
            monthly_spending[month_key] += amount

        # Top merchants
        merchant_totals[merchant] += amount

        # High value
        if amount >= high_value_threshold:
            high_value_transactions.append({
                "date": date_obj.strftime("%Y-%m-%d"),
                "amount": amount,
                "merchant": merchant,
                "description": description
            })

        # Recurring check (description + rounded amount)
        recurring_key = f"{description.strip().lower()}::{round(amount, -2)}"
        recurring_check[recurring_key].append(month_key)

    # Filter recurring transactions (appearing in >= 2 different months)
    recurring_transactions = {
        key.split("::")[0]: months
        for key, months in recurring_check.items()
        if len(set(months)) >= 2
    }

    # Top merchants (top 5)
    sorted_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    top_merchants = {merchant: round(total, 2) for merchant, total in sorted_merchants}

    insights = {
        "expense_breakdown": dict(expense_breakdown),
        "monthly_spending": dict(monthly_spending),
        "income_vs_expenses": {
            "income": dict(income_by_month),
            "expenses": dict(expenses_by_month)
        },
        "high_value_transactions": high_value_transactions,
        "recurring_transactions": recurring_transactions,
        "top_merchants": top_merchants
    }

    return insights