# 🚀 Clinic NL2SQL Chatbot

AI-powered Natural Language to SQL chatbot built using **Vanna AI 2.0**, **FastAPI**, and **Groq (llama-3.3-70b)**.

This system allows users to ask questions in plain English and automatically converts them into SQL queries, executes them on a SQLite database, and returns structured results.

---

## 🧠 Project Overview

User Question (English)
↓
FastAPI Backend (/chat endpoint)
↓
Vanna 2.0 Agent (Groq LLM)
↓
SQL Generation
↓
SQL Validation (safe SELECT queries only)
↓
SQLite Execution (clinic.db)
↓
Response (data + SQL + summary)

---

## ⚙️ Tech Stack

* Python 3.10+
* FastAPI
* Vanna AI 2.0
* Groq (llama-3.3-70b-versatile)
* SQLite
* Pandas
* Plotly

---

## 📁 Project Structure

clinic-nl2sql-chatbot/
│
├── main.py
├── setup_database.py
├── seed_memory.py
├── vanna_setup.py
├── requirements.txt
├── README.md
├── RESULTS.md
├── clinic.db
├── .gitignore
└── index.html

---

## 🚀 Setup Instructions

### 1. Clone Repository

git clone <your-repo-url>
cd clinic-nl2sql-chatbot

---

### 2. Create Virtual Environment

python -m venv venv
venv\Scripts\activate

---

### 3. Install Dependencies

pip install -r requirements.txt

---

### 4. Add API Key

Create `.env` file:
GROQ_API_KEY=your_api_key_here

---

### 5. Setup Database

python setup_database.py

---

### 6. Seed Memory

python seed_memory.py

---

### 7. Run Server

uvicorn main:app --port 8000 --reload

---

## 🌐 API Endpoints

### POST /chat

{
"question": "How many patients do we have?"
}

---

### GET /health

{
"status": "ok",
"database": "connected"
}

---

### GET /ui

Web-based chatbot interface.

---

## 🔐 SQL Validation

* Only SELECT queries allowed
* Blocks INSERT, UPDATE, DELETE, DROP
* Prevents unsafe execution

---

## ⚠️ Challenges Faced

* Groq API rate limits (free tier)
* Vanna 2.0 architecture learning curve
* Some complex queries failed (JOIN issues)
* Backend error handling limitations

---

## 💡 Future Improvements

* Add retry logic for API calls
* Improve SQL accuracy
* Add caching
* Enhance UI with charts

---

## 📌 Notes

* `.env` excluded for security
* `clinic.db` included as required
* Uses Groq free-tier LLM

---

## 🎯 Conclusion

This project demonstrates an end-to-end NL2SQL chatbot system handling real-world constraints effectively.
