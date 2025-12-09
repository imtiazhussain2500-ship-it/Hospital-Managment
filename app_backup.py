import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

DB_NAME = 'hospital.db'

st.set_page_config(page_title="🏥 Hospital Management System", page_icon="🏥", layout="wide")

st.markdown("""
<style>
    .main-header {font-size: 3rem; color: #2E86AB; text-align: center; margin-bottom: 2rem;}
    .metric-card {background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white;}
    .stButton > button {background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 5px; padding: 0.5rem 1rem;}
</style>
""", unsafe_allow_html=True)

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT 1")
    except sqlite3.DatabaseError:
        conn.close()
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS departments (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_name TEXT NOT NULL,
        location TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT,
        dept_id INTEGER,
        phone TEXT,
        email TEXT,
        experience INTEGER,
        consultation_fee REAL,
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        blood_group TEXT,
        registration_date DATE
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date DATE,
        appointment_time TEXT,
        status TEXT,
        reason TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    )''')
    
    c.execute("SELECT COUNT(*) FROM departments")
    if c.fetchone()[0] == 0:
        depts = [('Cardiology', 'Building A'), ('Neurology', 'Building B'), ('Orthopedics', 'Building C'), 
                 ('Pediatrics', 'Building D'), ('Emergency', 'Building E')]
        c.executemany("INSERT INTO departments (dept_name, location) VALUES (?, ?)", depts)
        
        doctors = [
            ('Dr. Ahmed Khan', 'Cardiologist', 1, '0300-1234567', 'ahmed@hospital.com', 15, 2000),
            ('Dr. Sara Ali', 'Neurologist', 2, '0301-2345678', 'sara@hospital.com', 10, 2500),
            ('Dr. Hassan Raza', 'Orthopedic Surgeon', 3, '0302-3456789', 'hassan@hospital.com', 12, 1800),
            ('Dr. Fatima Noor', 'Pediatrician', 4, '0303-4567890', 'fatima@hospital.com', 8, 1500),
            ('Dr. Usman Malik', 'Emergency Physician', 5, '0304-5678901', 'usman@hospital.com', 7, 1200)
        ]
        c.executemany("INSERT INTO doctors (name, specialization, dept_id, phone, email, experience, consultation_fee) VALUES (?, ?, ?, ?, ?, ?, ?)", doctors)
        
        patients = [
            ('Ali Hassan', 35, 'Male', '0311-1111111', 'ali@email.com', 'Karachi', 'O+', '2024-01-15'),
            ('Ayesha Khan', 28, 'Female', '0312-2222222', 'ayesha@email.com', 'Lahore', 'A+', '2024-01-20'),
            ('Bilal Ahmed', 42, 'Male', '0313-3333333', 'bilal@email.com', 'Islamabad', 'B+', '2024-02-10'),
            ('Zainab Ali', 55, 'Female', '0314-4444444', 'zainab@email.com', 'Karachi', 'AB+', '2024-02-15'),
            ('Hamza Malik', 30, 'Male', '0315-5555555', 'hamza@email.com', 'Lahore', 'O-', '2024-03-01')
        ]
        c.executemany("INSERT INTO patients (name, age, gender, phone, email, address, blood_group, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", patients)
        
        appointments = [
            (1, 1, '2024-03-15', '10:00 AM', 'Completed', 'Chest pain'),
            (2, 2, '2024-03-16', '11:00 AM', 'Completed', 'Headache'),
            (3, 3, '2024-03-17', '02:00 PM', 'Scheduled', 'Knee pain'),
            (4, 4, '2024-03-18', '09:00 AM', 'Scheduled', 'Child checkup'),
            (5, 5, '2024-03-19', '03:00 PM', 'Cancelled', 'Emergency')
        ]
        c.executemany("INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, reason) VALUES (?, ?, ?, ?, ?, ?)", appointments)
    
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    stats = {
        'patients': pd.read_sql("SELECT COUNT(*) as c FROM patients", conn).iloc[0]['c'],
        'doctors': pd.read_sql("SELECT COUNT(*) as c FROM doctors", conn).iloc[0]['c'],
        'appointments': pd.read_sql("SELECT COUNT(*) as c FROM appointments", conn).iloc[0]['c'],
        'pending': pd.read_sql("SELECT COUNT(*) as c FROM appointments WHERE status='Scheduled'", conn).iloc[0]['c']
    }
    conn.close()
    return stats

def ai_query(query):
    conn = sqlite3.connect(DB_NAME)
    query_lower = query.lower()
    
    try:
        if 'patient' in query_lower and 'count' in query_lower or 'how many patient' in query_lower:
            result = pd.read_sql("SELECT COUNT(*) as total FROM patients", conn)
            return f"Total Patients: {result.iloc[0]['total']}"
        
        elif 'doctor' in query_lower and ('most' in query_lower or 'top' in query_lower):
            result = pd.read_sql("""
                SELECT d.name, COUNT(a.appointment_id) as count
                FROM doctors d LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
                GROUP BY d.name ORDER BY count DESC LIMIT 1
            """, conn)
            return f"Top Doctor: {result.iloc[0]['name']} with {result.iloc[0]['count']} appointments"
        
        elif 'cardiology' in query_lower:
            result = pd.read_sql("""
                SELECT p.name, p.age, p.phone FROM patients p
                JOIN appointments a ON p.patient_id = a.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE d.specialization LIKE '%Cardio%'
            """, conn)
            return result.to_string() if not result.empty else "No cardiology patients found"
        
        elif 'fee' in query_lower and 'average' in query_lower:
            result = pd.read_sql("SELECT AVG(consultation_fee) as avg FROM doctors", conn)
            return f"Average Consultation Fee: Rs. {result.iloc[0]['avg']:.0f}"
        
        elif 'emergency' in query_lower:
            result = pd.read_sql("""
                SELECT p.name, a.appointment_date, a.reason FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE d.specialization LIKE '%Emergency%'
            """, conn)
            return result.to_string() if not result.empty else "No emergency appointments"
        
        else:
            return "I can answer: patient count, top doctor, cardiology patients, average fee, emergency appointments"
    
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()

init_db()

st.markdown('<h1 class="main-header">🏥 Hospital Management System</h1>', unsafe_allow_html=True)

st.sidebar.title("📋 Navigation")
page = st.sidebar.selectbox("Choose:", ["🏠 Dashboard", "💬 AI Chat", "👥 Patients", "👨⚕️ Doctors", "📅 Appointments", "📊 Analytics"])

if page == "🏠 Dashboard":
    st.header("📊 Dashboard")
    stats = get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Patients", stats['patients'])
    col2.metric("👨⚕️ Doctors", stats['doctors'])
    col3.metric("📅 Appointments", stats['appointments'])
    col4.metric("⏳ Pending", stats['pending'])
    
    st.divider()
    
    conn = sqlite3.connect(DB_NAME)
    
    col1, col2 = st.columns(2)
    with col1:
        dept_data = pd.read_sql("""
            SELECT d.dept_name, COUNT(a.appointment_id) as count
            FROM departments d
            LEFT JOIN doctors doc ON d.dept_id = doc.dept_id
            LEFT JOIN appointments a ON doc.doctor_id = a.doctor_id
            GROUP BY d.dept_name
        """, conn)
        if not dept_data.empty:
            fig = px.bar(dept_data, x='dept_name', y='count', title='Appointments by Department', color='count')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        age_data = pd.read_sql("SELECT age FROM patients", conn)
        if not age_data.empty:
            fig = px.histogram(age_data, x='age', title='Patient Age Distribution', nbins=10)
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🕒 Recent Appointments")
    recent = pd.read_sql("""
        SELECT p.name as Patient, d.name as Doctor, a.appointment_date as Date, 
               a.appointment_time as Time, a.status as Status, a.reason as Reason
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date DESC LIMIT 10
    """, conn)
    st.dataframe(recent, use_container_width=True)
    conn.close()

elif page == "💬 AI Chat":
    st.header("🤖 AI Chat")
    st.info("💡 Ask: 'How many patients?', 'Which doctor has most appointments?', 'Show cardiology patients', 'Average fee?', 'Emergency appointments'")
    
    query = st.text_input("💬 Your question:")
    if st.button("Ask") and query:
        with st.spinner("Thinking..."):
            response = ai_query(query)
            st.success(response)

elif page == "👥 Patients":
    st.header("👥 Patient Management")
    
    tab1, tab2 = st.tabs(["📋 View Patients", "➕ Add Patient"])
    
    with tab1:
        search = st.text_input("🔍 Search by name:")
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT * FROM patients"
        if search:
            query += f" WHERE name LIKE '%{search}%'"
        patients = pd.read_sql(query, conn)
        conn.close()
        st.dataframe(patients, use_container_width=True)
    
    with tab2:
        with st.form("add_patient"):
            name = st.text_input("Name*")
            col1, col2 = st.columns(2)
            age = col1.number_input("Age", 1, 120, 30)
            gender = col2.selectbox("Gender", ["Male", "Female", "Other"])
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            address = st.text_area("Address")
            blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            
            if st.form_submit_button("Add Patient"):
                if name:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO patients (name, age, gender, phone, email, address, blood_group, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (name, age, gender, phone, email, address, blood, datetime.now().strftime('%Y-%m-%d')))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Patient {name} added!")
                    st.rerun()
                else:
                    st.error("Name is required!")

elif page == "👨⚕️ Doctors":
    st.header("👨⚕️ Doctor Management")
    
    tab1, tab2 = st.tabs(["📋 View Doctors", "➕ Add Doctor"])
    
    with tab1:
        conn = sqlite3.connect(DB_NAME)
        doctors = pd.read_sql("""
            SELECT d.doctor_id, d.name, d.specialization, dept.dept_name, d.phone, 
                   d.email, d.experience, d.consultation_fee
            FROM doctors d
            LEFT JOIN departments dept ON d.dept_id = dept.dept_id
        """, conn)
        conn.close()
        st.dataframe(doctors, use_container_width=True)
    
    with tab2:
        with st.form("add_doctor"):
            name = st.text_input("Name*")
            spec = st.text_input("Specialization*")
            conn = sqlite3.connect(DB_NAME)
            depts = pd.read_sql("SELECT dept_id, dept_name FROM departments", conn)
            conn.close()
            dept = st.selectbox("Department", depts['dept_id'].tolist(), format_func=lambda x: depts[depts['dept_id']==x]['dept_name'].values[0])
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            exp = st.number_input("Experience (years)", 0, 50, 5)
            fee = st.number_input("Consultation Fee (Rs.)", 0, 10000, 1500)
            
            if st.form_submit_button("Add Doctor"):
                if name and spec:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO doctors (name, specialization, dept_id, phone, email, experience, consultation_fee) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (name, spec, dept, phone, email, exp, fee))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Doctor {name} added!")
                    st.rerun()
                else:
                    st.error("Name and Specialization required!")

elif page == "📅 Appointments":
    st.header("📅 Appointment Management")
    
    tab1, tab2 = st.tabs(["📋 View Appointments", "➕ Book Appointment"])
    
    with tab1:
        status_filter = st.selectbox("Filter by Status:", ["All", "Scheduled", "Completed", "Cancelled"])
        conn = sqlite3.connect(DB_NAME)
        query = """
            SELECT a.appointment_id, p.name as Patient, d.name as Doctor, 
                   a.appointment_date, a.appointment_time, a.status, a.reason
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
        """
        if status_filter != "All":
            query += f" WHERE a.status = '{status_filter}'"
        appointments = pd.read_sql(query, conn)
        conn.close()
        st.dataframe(appointments, use_container_width=True)
    
    with tab2:
        with st.form("book_appointment"):
            conn = sqlite3.connect(DB_NAME)
            patients = pd.read_sql("SELECT patient_id, name FROM patients", conn)
            doctors = pd.read_sql("SELECT doctor_id, name FROM doctors", conn)
            conn.close()
            
            patient = st.selectbox("Patient*", patients['patient_id'].tolist(), 
                                  format_func=lambda x: patients[patients['patient_id']==x]['name'].values[0])
            doctor = st.selectbox("Doctor*", doctors['doctor_id'].tolist(),
                                 format_func=lambda x: doctors[doctors['doctor_id']==x]['name'].values[0])
            date = st.date_input("Date*", datetime.now())
            time = st.time_input("Time*", datetime.now().time())
            reason = st.text_area("Reason")
            
            if st.form_submit_button("Book Appointment"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, reason) VALUES (?, ?, ?, ?, ?, ?)",
                         (patient, doctor, date.strftime('%Y-%m-%d'), time.strftime('%I:%M %p'), 'Scheduled', reason))
                conn.commit()
                conn.close()
                st.success("✅ Appointment booked!")
                st.rerun()

elif page == "📊 Analytics":
    st.header("📊 Advanced Analytics")
    
    conn = sqlite3.connect(DB_NAME)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Revenue by Doctor")
        revenue = pd.read_sql("""
            SELECT d.name, COUNT(a.appointment_id) * d.consultation_fee as revenue
            FROM doctors d
            LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
            WHERE a.status = 'Completed'
            GROUP BY d.name, d.consultation_fee
            ORDER BY revenue DESC
        """, conn)
        if not revenue.empty:
            fig = px.bar(revenue, x='name', y='revenue', title='Revenue by Doctor', color='revenue')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Appointment Status")
        status = pd.read_sql("SELECT status, COUNT(*) as count FROM appointments GROUP BY status", conn)
        if not status.empty:
            fig = px.pie(status, names='status', values='count', title='Appointment Status Distribution')
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🏥 Department Performance")
    dept_perf = pd.read_sql("""
        SELECT d.dept_name, COUNT(a.appointment_id) as appointments,
               SUM(doc.consultation_fee) as total_revenue
        FROM departments d
        LEFT JOIN doctors doc ON d.dept_id = doc.dept_id
        LEFT JOIN appointments a ON doc.doctor_id = a.doctor_id
        WHERE a.status = 'Completed'
        GROUP BY d.dept_name
    """, conn)
    st.dataframe(dept_perf, use_container_width=True)
    
    conn.close()

st.sidebar.divider()
st.sidebar.info("🏥 Hospital Management System v1.0")
