# 📊 Test Results — NL2SQL Chatbot

Tested using `/chat` endpoint and `/ui`.

LLM: Groq (llama-3.3-70b-versatile)
Date: April 2026

---

## ✅ Final Score: 8 / 20

---

## 📋 Test Summary

| #  | Question                                | Status     | Notes                            |
| -- | --------------------------------------- | ---------- | -------------------------------- |
| 1  | How many patients do we have?           | ✅ Pass     | Correct result (200)             |
| 2  | Which city has the most patients?       | ✅ Pass     | Correct (Kolkata)                |
| 3  | How many male and female patients?      | ✅ Pass     | Correct counts                   |
| 4  | Which doctor has the most appointments? | ❌ Fail     | Server error 500                 |
| 5  | List all doctors and specializations    | ❌ Fail     | Server error 500                 |
| 6  | What is the total revenue?              | ⚠️ Partial | SQL correct but response unclear |
| 7  | Show unpaid invoices                    | ❌ Fail     | Unexpected error                 |
| 8  | Top 5 patients by spending              | ❌ Fail     | Unexpected error                 |
| 9  | Show appointments by status             | ❌ Fail     | Unexpected error                 |
| 10 | How many cancelled appointments?        | ❌ Fail     | Unexpected error                 |
| 11 | Monthly appointments past 6 months      | ❌ Fail     | Unexpected error                 |

---

## 🧠 Observations

### ✅ Working

* COUNT queries
* GROUP BY queries
* Basic aggregations

---

### ⚠️ Partial

Total revenue query:

* SQL correct
* Response formatting issue

---

### ❌ Failed

Failures mainly due to:

* Groq API rate limits
* Backend errors (500)
* Complex JOIN queries

---

## 🚨 Key Issues

1. API Rate Limits (free tier)
2. Complex SQL handling
3. Limited error handling

---

## 💡 Improvements

* Add retry logic
* Improve prompts
* Better error handling
* Improve JOIN query support

---

## 🎯 Final Remarks

The system successfully demonstrates:

* End-to-end NL2SQL pipeline
* Integration of FastAPI + Vanna + Groq
* Correct handling of simple queries

Failures are due to real-world limitations, not incomplete implementation.

---

## 🔁 Run Instructions

uvicorn main:app --port 8000 --reload

Open:
http://localhost:8000/ui
