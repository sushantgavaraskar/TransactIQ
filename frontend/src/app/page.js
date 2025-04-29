'use client';

import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Pie, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from 'chart.js';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';


ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

export default function Home() {
  const [userId, setUserId] = useState('');
  const [file, setFile] = useState(null);
  const [insights, setInsights] = useState(null);
  const [statementId, setStatementId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [userInfo, setUserInfo] = useState(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setHydrated(true);
  }, []);

  if (!hydrated) return null;
  const handleUploadAndInsights = async () => {
    if (!file || !userId) {
      setStatus("Please enter User ID and select a file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);

    setLoading(true);
    setStatus("Uploading and analyzing...");

    try {
      const res = await fetch('http://127.0.0.1:8000/upload/', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (res.ok) {
        setStatementId(data.statement_id);
        setUserInfo(data.user);
        setStatus("Upload successful! Fetching insights...");
        await fetchInsights(data.statement_id);
      } else {
        setStatus(data.detail || "Upload failed.");
      }
    } catch (error) {
      console.error(error);
      setStatus("Error uploading file.");
    }
    setLoading(false);
  };

  const fetchInsights = async (id = null) => {
    const stmtId = id || statementId;
    if (!stmtId) {
      setStatus("No statement ID found.");
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/insights/statement/${stmtId}`);
      const data = await res.json();
      if (res.ok) {
        setInsights(data);
        setStatus("Insights loaded.");
      } else {
        setStatus("Failed to fetch insights.");
      }
    } catch (err) {
      console.error(err);
      setStatus("Error fetching insights.");
    }
  };
  const handleExportPDF = async () => {
  const input = document.getElementById('insights-section');
  if (!input) return;

  const canvas = await html2canvas(input, { scale: 2 });
  const imgData = canvas.toDataURL('image/png');
  const pdf = new jsPDF('p', 'mm', 'a4');
  const pdfWidth = pdf.internal.pageSize.getWidth();
  const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

  pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
  pdf.save('TransactIQ_Insights.pdf');
  };


  return (
    <div className="container mt-5">
      <h1 className="text-center text-primary mb-4">TransactIQ</h1>

      <div className="card shadow p-4 mb-4">
        <h4 className="mb-3">Upload Bank Statement</h4>
        <div className="mb-3">
          <label>User ID</label>
          <input
            type="number"
            className="form-control"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter User ID"
          />
        </div>
        <div className="mb-3">
          <label>Upload PDF</label>
          <input
            type="file"
            className="form-control"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>
        <div className="text-center">
          <button className="btn btn-success px-4" onClick={handleUploadAndInsights} disabled={loading}>
            {loading ? <span className="spinner-border spinner-border-sm me-2"></span> : null}
            Upload & Get Insights
          </button>
        </div>
        {status && (
          <div className="alert alert-info mt-3 py-2 text-center">{status}</div>
        )}
      </div>

      {userInfo && (
        <div className="alert alert-primary mb-4">
          <strong>User:</strong> {userInfo.name} | <strong>Email:</strong> {userInfo.email}
        </div>
      )}

      {insights && (
        <div id="insights-section" className="card shadow p-4 mb-5">
          <h4 className="text-info mb-4 text-center">📊 Financial Insights</h4>
                  <div className="text-end mb-3">
          <button className="btn btn-danger" onClick={handleExportPDF}>
            📄 Export as PDF
          </button>
        </div>

          <div className="row">
            <div className="col-md-6 mb-4">
              <ChartSection title="💸 Expense Breakdown" type="pie" data={insights.expense_breakdown} />
            </div>
            <div className="col-md-6 mb-4">
              <ChartSection title="📅 Monthly Spending" type="bar" data={insights.monthly_spending} />
            </div>
            <div className="col-md-12 mb-4">
              <ChartSection title="📊 Income vs Expenses" type="groupedBar" data={insights.income_vs_expenses} />
            </div>
          </div>

          <div className="row">
            <div className="col-md-6">
              <InsightSection title="🏦 High-Value Transactions" data={insights.high_value_transactions} />
            </div>
            <div className="col-md-6">
              <InsightSection title="🔁 Recurring Transactions" data={insights.recurring_transactions} />
            </div>
          </div>

          <div className="row mt-4">
            <div className="col-md-12">
              <TopMerchantsSection merchants={insights.top_merchants} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function InsightSection({ title, data }) {
  const isEmpty = !data || (Array.isArray(data) && data.length === 0) || (typeof data === 'object' && Object.keys(data).length === 0);
  return (
    <div className="mb-4">
      <h5 className="text-secondary">{title}</h5>
      {isEmpty ? (
        <div className="alert alert-warning">No data available.</div>
      ) : (
        <pre className="bg-light p-3 rounded">{JSON.stringify(data, null, 2)}</pre>
      )}
    </div>
  );
}

function ChartSection({ title, type, data }) {
  if (!data || typeof data !== 'object') return null;

  const labels =
    type === 'groupedBar'
      ? [...new Set([...Object.keys(data.income || {}), ...Object.keys(data.expenses || {})])]
      : Object.keys(data);

  const chartData =
    type === 'groupedBar'
      ? {
          labels,
          datasets: [
            { label: 'Income', data: labels.map(l => data.income[l] || 0), backgroundColor: '#4CAF50' },
            { label: 'Expenses', data: labels.map(l => data.expenses[l] || 0), backgroundColor: '#F44336' },
          ],
        }
      : {
          labels,
          datasets: [{
            label: title,
            data: Object.values(data),
            backgroundColor: type === 'pie'
              ? ['#FF6384', '#36A2EB', '#FFCE56', '#8BC34A', '#FF9800']
              : '#42A5F5',
          }],
        };

  return (
    <div className="mb-4">
      <h5 className="text-secondary mb-3">{title}</h5>
      {type === 'pie' && <Pie data={chartData} />}
      {type === 'bar' && <Bar data={chartData} />}
      {type === 'groupedBar' && <Bar data={chartData} />}
    </div>
  );
}

function TopMerchantsSection({ merchants }) {
  if (!merchants || Object.keys(merchants).length === 0) {
    return (
      <div className="mb-4">
        <h5 className="text-secondary">🏪 Top Merchants</h5>
        <div className="alert alert-warning">No merchant data found.</div>
      </div>
    );
  }

  return (
    <div className="mb-4">
      <h5 className="text-secondary">🏪 Top Merchants</h5>
      <table className="table table-bordered table-striped">
        <thead className="table-dark">
          <tr>
            <th>Merchant</th>
            <th>Total Spent (₹)</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(merchants).map(([merchant, amount], i) => (
            <tr key={i}>
              <td>{merchant}</td>
              <td>₹{amount.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
