from fpdf import FPDF
import random
from datetime import datetime, timedelta

# Helper to generate random transactions
def generate_transaction(date, txn_type, amount, balance, ref_no):
    if txn_type in ['Cash Deposit', 'Interest Credit']:
        debit = ''
        credit = f"{amount:,.2f}"
        balance += amount
    else:
        debit = f"{amount:,.2f}"/8989/89/+98/99
        credit = ''
        balance -= amount
    return {
        "date": date.strftime('%d-%m-%Y'),
        "particulars": txn_type,
        "ref_no": str(ref_no),
        "debit": debit,
        "credit": credit,
        "balance": f"{balance:,.2f}"
    }, balance

# Create PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Header
pdf.set_font("Arial", style='B', size=16)
pdf.cell(200, 10, "GHI Bank", ln=True, align='C')
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, "Account Statement", ln=True, align='C')
pdf.ln(5)
pdf.cell(200, 10, "Account No: 1041084940     Branch: Suburban Branch", ln=True)
pdf.cell(200, 10, "IFSC Code: GHI654321     MICR Code: 567890123", ln=True)
pdf.cell(200, 10, "CIF No: 156025849     Interest Rate: 3.22%", ln=True)
pdf.cell(200, 10, f"Balance as on: {datetime.today().strftime('%d %b %Y')}", ln=True)

pdf.ln(10)
pdf.set_font("Arial", style='B', size=12)
pdf.cell(35, 10, "Date", 1)
pdf.cell(45, 10, "Particulars", 1)
pdf.cell(40, 10, "Reference No", 1)
pdf.cell(25, 10, "Debit (Rs)", 1)
pdf.cell(25, 10, "Credit (Rs)", 1)
pdf.cell(30, 10, "Balance (Rs)", 1)

# Sample transactions
pdf.set_font("Arial", size=11)
start_date = datetime(2024, 2, 1)
balance = 50000.00
ref_base = 700000000000

txn_types = [
    'UPI Transfer', 'NEFT Transfer', 'Cash Deposit', 'ATM Withdrawal',
    'Interest Credit', 'Online Purchase', 'POS Transaction', 'EMI Payment'
]

for i in range(30):
    txn_type = random.choice(txn_types)
    amount = round(random.uniform(2000, 50000), 2)
    ref_no = ref_base + i
    date = start_date + timedelta(days=random.randint(0, 400))
    txn, balance = generate_transaction(date, txn_type, amount, balance, ref_no)

    pdf.cell(35, 10, txn["date"], 1)
    pdf.cell(45, 10, txn["particulars"], 1)
    pdf.cell(40, 10, txn["ref_no"], 1)
    pdf.cell(25, 10, txn["debit"], 1)
    pdf.cell(25, 10, txn["credit"], 1)
    pdf.cell(30, 10, txn["balance"], 1)
    pdf.ln()

# Save PDF
pdf.output("sample_bank_statement.pdf")
print("✅ Sample bank statement generated: sample_bank_statement.pdf")
