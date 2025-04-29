import re
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datetime import datetime

# ✅ Load Pre-trained NLP Model for Transaction Categorization
MODEL_NAME = "kuro-08/bert-transaction-categorization"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# ✅ Correct Category Mapping (Consistent across all files)
CATEGORIES = {
    0: "Utilities",
    1: "Health",
    2: "Dining",
    3: "Travel",
    4: "Education",
    5: "Subscription",
    6: "Family",
    7: "Food",
    8: "Festivals",
    9: "Culture",
    10: "Apparel",
    11: "Transportation",
    12: "Investment",
    13: "Shopping",
    14: "Groceries",
    15: "Documents",
    16: "Grooming",
    17: "Entertainment",
    18: "Social Life",
    19: "Beauty",
    20: "Rent",
    21: "Money transfer",
    22: "Salary",
    23: "Tourism",
    24: "Household",
}

def categorize_transaction(description: str):
    """
    Uses a fine-tuned BERT model to categorize a transaction based on its description.
    """
    try:
        if not description.strip():
            return "Uncategorized"

        inputs = tokenizer(description, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():  # ✅ Ensure no gradient tracking
            outputs = model(**inputs)

        predicted_idx = torch.argmax(outputs.logits, dim=-1).item()
        
        # ✅ Debugging Log
        print(f"🔍 Predicted index: {predicted_idx}, Category: {CATEGORIES.get(predicted_idx, 'Uncategorized')}")

        return CATEGORIES.get(predicted_idx, "Uncategorized")

    except Exception as e:
        print(f"❌ Error predicting category: {str(e)}")
        return "Uncategorized"  # Fallback category

def extract_transactions(ocr_text: str):
    """
    Extracts transaction details from OCR-extracted text.
    """
    transactions = []
    lines = ocr_text.split("\n")

    for line in lines:
        match = re.search(r"(\d{2}-\d{2}-\d{4})\s+([\w\s]+?)\s+(-?\d+\.\d{2})", line)
        if match:
            transaction_date = datetime.strptime(match.group(1), "%d-%m-%Y")
            description = match.group(2).strip()
            amount = abs(float(match.group(3)))
            transaction_type = "Credit" if float(match.group(3)) > 0 else "Debit"
            category = categorize_transaction(description)  # ✅ Assign category using BERT model

            transactions.append({
                "transaction_date": transaction_date,
                "description": description,
                "amount": amount,
                "transaction_type": transaction_type,
                "category": category
            })

    return transactions
