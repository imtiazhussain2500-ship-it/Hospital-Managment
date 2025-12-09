# 🏥 Hospital Management System - Advanced Edition

A complete enterprise-grade hospital management system built with Streamlit and SQLite.

## ✨ Features

### Core Modules
- 🏠 **Dashboard** - Real-time statistics and visualizations
- 💬 **AI Chat** - Natural language queries (no API key needed)
- 👥 **Patient Management** - Add, view, search patients
- 👨⚕️ **Doctor Management** - Manage doctor profiles
- 📅 **Appointments** - Book and track appointments
- 📊 **Analytics** - Revenue and performance metrics

### Advanced Modules
- 📋 **Medical Records** - Patient diagnosis, prescriptions, and notes
- 💰 **Billing System** - Invoice generation and payment tracking
- 👷 **Staff Management** - Employee records and salary management
- 📦 **Inventory** - Medical supplies and equipment tracking

### Enterprise Modules
- 🛏️ **Bed Management** - IPD/OPD bed allocation and tracking
- 🔬 **Lab Tests** - Laboratory test orders and results
- 💊 **Pharmacy** - Medicine dispensing and prescription management
- 🚑 **Ambulance** - Emergency vehicle dispatch and tracking
- 🩸 **Blood Bank** - Blood donation and inventory management

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**
   ```bash
   streamlit run app.py
   ```

3. **Access** - Opens automatically at `http://localhost:8501`

## 💡 AI Chat Examples

### Basic Queries
- "How many patients?"
- "Which doctor has most appointments?"
- "Show cardiology patients"
- "What's the average fee?"
- "List emergency appointments"

### Advanced Queries
- "Total revenue?"
- "How many staff members?"
- "Show pending bills"
- "Low stock items?"

## 📁 Files

- `app.py` - Main application (includes database setup)
- `requirements.txt` - Python dependencies
- `README.md` - Documentation
- `hospital.db` - SQLite database (auto-created)

## 🗄️ Database

Auto-initializes with sample data:
- 5 Departments
- 5 Doctors
- 5 Patients
- 5 Appointments
- 2 Medical Records
- 3 Billing Entries
- 3 Staff Members
- 4 Inventory Items
- 5 Beds (General, ICU, Private)
- 3 Lab Tests
- 3 Pharmacy Records
- 3 Ambulances
- 5 Blood Bank Entries

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite3
- **Visualization**: Plotly
- **Data**: Pandas

## 📝 Notes

- No external API keys required
- Sample data included
- Fully functional offline
- Mobile responsive

## 🔧 Troubleshooting

If you get errors:
```bash
pip install --upgrade streamlit pandas plotly
```

Then run:
```bash
streamlit run app.py
```
