# TransactIQ - Smart Bank Statement Reader

**TransactIQ** is a full-stack intelligent platform where users can upload bank statement PDFs, extract and categorize transactions using OCR and NLP, and view meaningful financial insights through visual dashboards.

## Project Features

- Upload scanned or text-based PDF bank statements
- Extract transactions using Tesseract OCR
- Automatically categorize transactions using a BERT-based model
- Store user-specific transactions in a PostgreSQL database
- Generate visual financial insights:
  - Expense breakdown by category
  - Monthly spending trends
  - Income vs expenses comparison
  - Recurring transactions
  - High-value transactions
  - Top merchants
- Frontend built with Next.js and Bootstrap
- Download insights as PDF report
- Dark mode toggle and single-click dashboard interface

## Tech Stack

| Component     | Technology                             |
|---------------|-----------------------------------------|
| Backend       | FastAPI (Python)                        |
| OCR           | Tesseract OCR                           |
| NLP Model     | kuro-08/bert-transaction-categorization |
| Database      | PostgreSQL + SQLAlchemy ORM             |
| Frontend      | Next.js with Bootstrap                  |
| Charting      | Chart.js                                |
| PDF Export    | html2canvas + jsPDF                     |

## Folder Structure

```
TransactIQ/
│
├── backend/
│   ├── main.py             # API routes
│   ├── models.py           # Database models
│   ├── crud.py             # DB logic
│   ├── preprocess.py       # Text + NLP processing
│   ├── ocr.py              # OCR logic
│   ├── database.py         # DB connection setup
│   └── uploads/            # Uploaded PDFs
│
├── frontend/
│   └── src/app/page.js     # Main UI
│
└── README.md               # Project documentation
```

## Setup Instructions

### Backend (FastAPI)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/transactiq.git
   cd transactiq/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Update database credentials in `database.py`.

5. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

Backend runs at: `http://127.0.0.1:8000`

### Frontend (Next.js)

1. Navigate to the frontend:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the frontend development server:
   ```bash
   npm run dev
   ```

Frontend runs at: `http://localhost:3000`

## Usage Workflow

1. The user inputs their user ID and uploads a PDF bank statement.
2. The backend extracts and categorizes transaction data.
3. Transaction records are saved in the database linked to the user.
4. Insights are fetched and visualized on the frontend using charts and tables.
5. Users can export their insights as a downloadable PDF report.

## Known Limitations

- Processing large PDFs can take 7–10 seconds per page.
- OCR may fail on low-quality scans or handwritten data.
- BERT model may misclassify some edge-case transactions.
- No advanced authentication system implemented.
- Limited to basic insights; predictive analytics not yet integrated.

## Future Enhancements

- Add JWT-based user authentication
- Improve processing speed using async and caching
- Expand BERT training data for better classification
- Introduce budgeting and forecasting features
- Create a mobile-friendly version or app

## Contributors

- Sushant Gavaraskar  

