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
    
    c.execute('''CREATE TABLE IF NOT EXISTS medical_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        diagnosis TEXT,
        prescription TEXT,
        notes TEXT,
        record_date DATE,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS billing (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        appointment_id INTEGER,
        amount REAL,
        payment_status TEXT,
        payment_date DATE,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT,
        dept_id INTEGER,
        phone TEXT,
        email TEXT,
        salary REAL,
        join_date DATE,
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        category TEXT,
        quantity INTEGER,
        unit_price REAL,
        supplier TEXT,
        last_updated DATE
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS beds (
        bed_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bed_number TEXT NOT NULL,
        ward_type TEXT,
        status TEXT,
        patient_id INTEGER,
        admission_date DATE,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS lab_tests (
        test_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        test_name TEXT,
        test_date DATE,
        result TEXT,
        status TEXT,
        cost REAL,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pharmacy (
        prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        medicine_name TEXT,
        dosage TEXT,
        quantity INTEGER,
        price REAL,
        issue_date DATE,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ambulance (
        ambulance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT,
        driver_name TEXT,
        status TEXT,
        patient_id INTEGER,
        pickup_location TEXT,
        destination TEXT,
        request_time DATETIME,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS blood_bank (
        blood_id INTEGER PRIMARY KEY AUTOINCREMENT,
        blood_group TEXT,
        units INTEGER,
        donor_name TEXT,
        donation_date DATE,
        expiry_date DATE
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
        
        medical_records = [
            (1, 1, 'Angina Pectoris', 'Aspirin 75mg, Atorvastatin 20mg', 'Patient advised rest', '2024-03-15'),
            (2, 2, 'Migraine', 'Sumatriptan 50mg', 'Avoid stress triggers', '2024-03-16')
        ]
        c.executemany("INSERT INTO medical_records (patient_id, doctor_id, diagnosis, prescription, notes, record_date) VALUES (?, ?, ?, ?, ?, ?)", medical_records)
        
        billing = [
            (1, 1, 2000, 'Paid', '2024-03-15'),
            (2, 2, 2500, 'Paid', '2024-03-16'),
            (3, 3, 1800, 'Pending', None)
        ]
        c.executemany("INSERT INTO billing (patient_id, appointment_id, amount, payment_status, payment_date) VALUES (?, ?, ?, ?, ?)", billing)
        
        staff = [
            ('Nurse Sarah', 'Nurse', 1, '0320-1111111', 'sarah.nurse@hospital.com', 50000, '2023-01-10'),
            ('Receptionist Ali', 'Receptionist', 5, '0321-2222222', 'ali.reception@hospital.com', 35000, '2023-05-15'),
            ('Lab Tech Hassan', 'Lab Technician', 2, '0322-3333333', 'hassan.lab@hospital.com', 45000, '2023-03-20')
        ]
        c.executemany("INSERT INTO staff (name, role, dept_id, phone, email, salary, join_date) VALUES (?, ?, ?, ?, ?, ?, ?)", staff)
        
        inventory = [
            ('Paracetamol', 'Medicine', 500, 5, 'PharmaCorp', '2024-03-01'),
            ('Surgical Gloves', 'Equipment', 200, 50, 'MedSupply', '2024-03-05'),
            ('Syringes', 'Equipment', 1000, 10, 'MedSupply', '2024-03-10'),
            ('Bandages', 'Supplies', 300, 20, 'HealthCare Ltd', '2024-03-12')
        ]
        c.executemany("INSERT INTO inventory (item_name, category, quantity, unit_price, supplier, last_updated) VALUES (?, ?, ?, ?, ?, ?)", inventory)
        
        beds = [
            ('B-101', 'General', 'Occupied', 1, '2024-03-15'),
            ('B-102', 'General', 'Available', None, None),
            ('B-201', 'ICU', 'Occupied', 2, '2024-03-16'),
            ('B-202', 'ICU', 'Available', None, None),
            ('B-301', 'Private', 'Available', None, None)
        ]
        c.executemany("INSERT INTO beds (bed_number, ward_type, status, patient_id, admission_date) VALUES (?, ?, ?, ?, ?)", beds)
        
        lab_tests = [
            (1, 'Blood Test', '2024-03-15', 'Normal', 'Completed', 1500),
            (2, 'MRI Scan', '2024-03-16', 'Pending', 'In Progress', 8000),
            (3, 'X-Ray', '2024-03-17', None, 'Scheduled', 2000)
        ]
        c.executemany("INSERT INTO lab_tests (patient_id, test_name, test_date, result, status, cost) VALUES (?, ?, ?, ?, ?, ?)", lab_tests)
        
        pharmacy = [
            (1, 1, 'Aspirin', '75mg', 30, 150, '2024-03-15'),
            (2, 2, 'Sumatriptan', '50mg', 10, 500, '2024-03-16'),
            (3, 3, 'Ibuprofen', '400mg', 20, 200, '2024-03-17')
        ]
        c.executemany("INSERT INTO pharmacy (patient_id, doctor_id, medicine_name, dosage, quantity, price, issue_date) VALUES (?, ?, ?, ?, ?, ?, ?)", pharmacy)
        
        ambulance = [
            ('AMB-001', 'Rashid Khan', 'Available', None, None, None, None),
            ('AMB-002', 'Imran Ali', 'On Duty', 5, 'Gulshan', 'Hospital', '2024-03-19 15:30:00'),
            ('AMB-003', 'Salman Ahmed', 'Available', None, None, None, None)
        ]
        c.executemany("INSERT INTO ambulance (vehicle_number, driver_name, status, patient_id, pickup_location, destination, request_time) VALUES (?, ?, ?, ?, ?, ?, ?)", ambulance)
        
        blood_bank = [
            ('A+', 15, 'Donor 1', '2024-03-01', '2024-06-01'),
            ('B+', 10, 'Donor 2', '2024-03-05', '2024-06-05'),
            ('O+', 20, 'Donor 3', '2024-03-10', '2024-06-10'),
            ('AB+', 5, 'Donor 4', '2024-03-12', '2024-06-12'),
            ('O-', 8, 'Donor 5', '2024-03-14', '2024-06-14')
        ]
        c.executemany("INSERT INTO blood_bank (blood_group, units, donor_name, donation_date, expiry_date) VALUES (?, ?, ?, ?, ?)", blood_bank)
    
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    stats = {
        'patients': pd.read_sql("SELECT COUNT(*) as c FROM patients", conn).iloc[0]['c'],
        'doctors': pd.read_sql("SELECT COUNT(*) as c FROM doctors", conn).iloc[0]['c'],
        'appointments': pd.read_sql("SELECT COUNT(*) as c FROM appointments", conn).iloc[0]['c'],
        'pending': pd.read_sql("SELECT COUNT(*) as c FROM appointments WHERE status='Scheduled'", conn).iloc[0]['c'],
        'staff': pd.read_sql("SELECT COUNT(*) as c FROM staff", conn).iloc[0]['c'],
        'revenue': pd.read_sql("SELECT SUM(amount) as c FROM billing WHERE payment_status='Paid'", conn).iloc[0]['c'] or 0,
        'pending_bills': pd.read_sql("SELECT COUNT(*) as c FROM billing WHERE payment_status='Pending'", conn).iloc[0]['c'],
        'available_beds': pd.read_sql("SELECT COUNT(*) as c FROM beds WHERE status='Available'", conn).iloc[0]['c'],
        'occupied_beds': pd.read_sql("SELECT COUNT(*) as c FROM beds WHERE status='Occupied'", conn).iloc[0]['c'],
        'pending_tests': pd.read_sql("SELECT COUNT(*) as c FROM lab_tests WHERE status!='Completed'", conn).iloc[0]['c'],
        'ambulance_available': pd.read_sql("SELECT COUNT(*) as c FROM ambulance WHERE status='Available'", conn).iloc[0]['c']
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
        
        elif 'revenue' in query_lower or 'income' in query_lower:
            result = pd.read_sql("SELECT SUM(amount) as total FROM billing WHERE payment_status='Paid'", conn)
            return f"Total Revenue: Rs. {result.iloc[0]['total']:,.0f}"
        
        elif 'staff' in query_lower and 'count' in query_lower:
            result = pd.read_sql("SELECT COUNT(*) as total FROM staff", conn)
            return f"Total Staff: {result.iloc[0]['total']}"
        
        elif 'pending' in query_lower and 'bill' in query_lower:
            result = pd.read_sql("SELECT COUNT(*) as total, SUM(amount) as amount FROM billing WHERE payment_status='Pending'", conn)
            return f"Pending Bills: {result.iloc[0]['total']} (Rs. {result.iloc[0]['amount']:,.0f})"
        
        elif 'inventory' in query_lower or 'stock' in query_lower:
            result = pd.read_sql("SELECT COUNT(*) as total FROM inventory WHERE quantity < 100", conn)
            return f"Low Stock Items: {result.iloc[0]['total']}"
        
        else:
            return "I can answer: patient count, top doctor, cardiology patients, average fee, emergency appointments, revenue, staff count, pending bills, inventory status"
    
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()

init_db()

st.markdown('<h1 class="main-header">🏥 Hospital Management System</h1>', unsafe_allow_html=True)

st.sidebar.title("📋 Navigation")
page = st.sidebar.selectbox("Choose:", ["🏠 Dashboard", "💬 AI Chat", "👥 Patients", "👨⚕️ Doctors", "📅 Appointments", "📊 Analytics", "📋 Medical Records", "💰 Billing", "👷 Staff", "📦 Inventory", "🛏️ Bed Management", "🔬 Lab Tests", "💊 Pharmacy", "🚑 Ambulance", "🩸 Blood Bank"])

if page == "🏠 Dashboard":
    st.header("📊 Dashboard")
    stats = get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Patients", stats['patients'])
    col2.metric("👨⚕️ Doctors", stats['doctors'])
    col3.metric("📅 Appointments", stats['appointments'])
    col4.metric("⏳ Pending", stats['pending'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👷 Staff", stats['staff'])
    col2.metric("💰 Revenue", f"Rs. {stats['revenue']:,.0f}")
    col3.metric("📋 Pending Bills", stats['pending_bills'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🛏️ Available Beds", stats['available_beds'])
    col2.metric("🛌 Occupied Beds", stats['occupied_beds'])
    col3.metric("🔬 Pending Tests", stats['pending_tests'])
    col4.metric("🚑 Ambulances", stats['ambulance_available'])
    
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
    
    st.subheader("🏥 Hospital Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛏️ Bed Status")
        beds = pd.read_sql("""
            SELECT b.bed_number, b.ward_type, b.status, p.name as patient_name
            FROM beds b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            ORDER BY b.bed_number
        """, conn)
        st.dataframe(beds, use_container_width=True)
    
    with col2:
        st.markdown("### 🔬 Lab Tests Status")
        lab_tests = pd.read_sql("""
            SELECT p.name as Patient, l.test_name as Test, l.status as Status, l.test_date as Date
            FROM lab_tests l
            JOIN patients p ON l.patient_id = p.patient_id
            ORDER BY l.test_date DESC
        """, conn)
        st.dataframe(lab_tests, use_container_width=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚑 Ambulance Fleet")
        ambulances = pd.read_sql("""
            SELECT a.vehicle_number as Vehicle, a.driver_name as Driver, 
                   a.status as Status, p.name as Patient
            FROM ambulance a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
        """, conn)
        st.dataframe(ambulances, use_container_width=True)
    
    with col2:
        st.markdown("### 🩸 Blood Bank Stock")
        blood = pd.read_sql("""
            SELECT blood_group as 'Blood Group', SUM(units) as 'Total Units'
            FROM blood_bank
            GROUP BY blood_group
            ORDER BY blood_group
        """, conn)
        st.dataframe(blood, use_container_width=True)
    
    st.divider()
    
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
    st.header("🤖 AI Chat Assistant")
    st.info("💡 Ask: 'How many patients?', 'Top doctor?', 'Show cardiology patients', 'Average fee?', 'Total revenue?', 'Staff count?', 'Pending bills?', 'Low stock items?'")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("👥 Patients"):
            st.session_state['ai_response'] = ai_query("How many patients?")
    with col2:
        if st.button("💰 Revenue"):
            st.session_state['ai_response'] = ai_query("Total revenue")
    with col3:
        if st.button("💵 Pending Bills"):
            st.session_state['ai_response'] = ai_query("Pending bills")
    with col4:
        if st.button("📦 Low Stock"):
            st.session_state['ai_response'] = ai_query("Low stock items")
    
    if 'ai_response' in st.session_state:
        st.success(st.session_state['ai_response'])
    
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

elif page == "📋 Medical Records":
    st.header("📋 Medical Records")
    
    tab1, tab2 = st.tabs(["📊 View Records", "➕ Add Record"])
    
    with tab1:
        conn = sqlite3.connect(DB_NAME)
        records = pd.read_sql("""
            SELECT m.record_id, p.name as Patient, d.name as Doctor, 
                   m.diagnosis, m.prescription, m.notes, m.record_date
            FROM medical_records m
            JOIN patients p ON m.patient_id = p.patient_id
            JOIN doctors d ON m.doctor_id = d.doctor_id
            ORDER BY m.record_date DESC
        """, conn)
        conn.close()
        st.dataframe(records, use_container_width=True)
    
    with tab2:
        with st.form("add_record"):
            conn = sqlite3.connect(DB_NAME)
            patients = pd.read_sql("SELECT patient_id, name FROM patients", conn)
            doctors = pd.read_sql("SELECT doctor_id, name FROM doctors", conn)
            conn.close()
            
            patient = st.selectbox("Patient*", patients['patient_id'].tolist(), 
                                  format_func=lambda x: patients[patients['patient_id']==x]['name'].values[0])
            doctor = st.selectbox("Doctor*", doctors['doctor_id'].tolist(),
                                 format_func=lambda x: doctors[doctors['doctor_id']==x]['name'].values[0])
            diagnosis = st.text_input("Diagnosis*")
            prescription = st.text_area("Prescription")
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Add Record"):
                if diagnosis:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO medical_records (patient_id, doctor_id, diagnosis, prescription, notes, record_date) VALUES (?, ?, ?, ?, ?, ?)",
                             (patient, doctor, diagnosis, prescription, notes, datetime.now().strftime('%Y-%m-%d')))
                    conn.commit()
                    conn.close()
                    st.success("✅ Medical record added!")
                    st.rerun()
                else:
                    st.error("Diagnosis is required!")

elif page == "💰 Billing":
    st.header("💰 Billing Management")
    
    tab1, tab2, tab3 = st.tabs(["📊 View Bills", "➕ Create Bill", "💳 Payment"])
    
    with tab1:
        status_filter = st.selectbox("Filter:", ["All", "Paid", "Pending"])
        conn = sqlite3.connect(DB_NAME)
        query = """
            SELECT b.bill_id, p.name as Patient, a.appointment_date, 
                   b.amount, b.payment_status, b.payment_date
            FROM billing b
            JOIN patients p ON b.patient_id = p.patient_id
            LEFT JOIN appointments a ON b.appointment_id = a.appointment_id
        """
        if status_filter != "All":
            query += f" WHERE b.payment_status = '{status_filter}'"
        bills = pd.read_sql(query, conn)
        conn.close()
        
        if not bills.empty:
            st.dataframe(bills, use_container_width=True)
            total = bills['amount'].sum()
            paid = bills[bills['payment_status']=='Paid']['amount'].sum() if 'Paid' in bills['payment_status'].values else 0
            pending = bills[bills['payment_status']=='Pending']['amount'].sum() if 'Pending' in bills['payment_status'].values else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("💵 Total", f"Rs. {total:,.0f}")
            col2.metric("✅ Paid", f"Rs. {paid:,.0f}")
            col3.metric("⏳ Pending", f"Rs. {pending:,.0f}")
    
    with tab2:
        with st.form("create_bill"):
            conn = sqlite3.connect(DB_NAME)
            patients = pd.read_sql("SELECT patient_id, name FROM patients", conn)
            appointments = pd.read_sql("SELECT appointment_id, patient_id, appointment_date FROM appointments", conn)
            conn.close()
            
            patient = st.selectbox("Patient*", patients['patient_id'].tolist(), 
                                  format_func=lambda x: patients[patients['patient_id']==x]['name'].values[0])
            appointment = st.selectbox("Appointment", appointments['appointment_id'].tolist(),
                                      format_func=lambda x: f"ID: {x} - {appointments[appointments['appointment_id']==x]['appointment_date'].values[0]}")
            amount = st.number_input("Amount (Rs.)*", 0, 100000, 1000)
            
            if st.form_submit_button("Create Bill"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO billing (patient_id, appointment_id, amount, payment_status, payment_date) VALUES (?, ?, ?, ?, ?)",
                         (patient, appointment, amount, 'Pending', None))
                conn.commit()
                conn.close()
                st.success("✅ Bill created!")
                st.rerun()
    
    with tab3:
        conn = sqlite3.connect(DB_NAME)
        pending_bills = pd.read_sql("""
            SELECT b.bill_id, p.name, b.amount
            FROM billing b
            JOIN patients p ON b.patient_id = p.patient_id
            WHERE b.payment_status = 'Pending'
        """, conn)
        conn.close()
        
        if not pending_bills.empty:
            bill_id = st.selectbox("Select Bill to Pay", pending_bills['bill_id'].tolist(),
                                  format_func=lambda x: f"Bill #{x} - {pending_bills[pending_bills['bill_id']==x]['name'].values[0]} - Rs. {pending_bills[pending_bills['bill_id']==x]['amount'].values[0]}")
            
            if st.button("💳 Mark as Paid"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("UPDATE billing SET payment_status='Paid', payment_date=? WHERE bill_id=?",
                         (datetime.now().strftime('%Y-%m-%d'), bill_id))
                conn.commit()
                conn.close()
                st.success("✅ Payment recorded!")
                st.rerun()
        else:
            st.info("No pending bills")

elif page == "👷 Staff":
    st.header("👷 Staff Management")
    
    tab1, tab2 = st.tabs(["📊 View Staff", "➕ Add Staff"])
    
    with tab1:
        conn = sqlite3.connect(DB_NAME)
        staff = pd.read_sql("""
            SELECT s.staff_id, s.name, s.role, d.dept_name, s.phone, s.email, s.salary, s.join_date
            FROM staff s
            LEFT JOIN departments d ON s.dept_id = d.dept_id
        """, conn)
        conn.close()
        st.dataframe(staff, use_container_width=True)
        
        if not staff.empty:
            total_salary = staff['salary'].sum()
            st.metric("💰 Total Monthly Salary", f"Rs. {total_salary:,.0f}")
    
    with tab2:
        with st.form("add_staff"):
            name = st.text_input("Name*")
            role = st.selectbox("Role*", ["Nurse", "Receptionist", "Lab Technician", "Pharmacist", "Cleaner", "Security", "Admin"])
            conn = sqlite3.connect(DB_NAME)
            depts = pd.read_sql("SELECT dept_id, dept_name FROM departments", conn)
            conn.close()
            dept = st.selectbox("Department", depts['dept_id'].tolist(), format_func=lambda x: depts[depts['dept_id']==x]['dept_name'].values[0])
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            salary = st.number_input("Salary (Rs.)", 0, 200000, 40000)
            
            if st.form_submit_button("Add Staff"):
                if name:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO staff (name, role, dept_id, phone, email, salary, join_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (name, role, dept, phone, email, salary, datetime.now().strftime('%Y-%m-%d')))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Staff {name} added!")
                    st.rerun()
                else:
                    st.error("Name is required!")

elif page == "📦 Inventory":
    st.header("📦 Inventory Management")
    
    tab1, tab2, tab3 = st.tabs(["📊 View Inventory", "➕ Add Item", "🔄 Update Stock"])
    
    with tab1:
        conn = sqlite3.connect(DB_NAME)
        inventory = pd.read_sql("SELECT * FROM inventory ORDER BY item_name", conn)
        conn.close()
        st.dataframe(inventory, use_container_width=True)
        
        if not inventory.empty:
            low_stock = inventory[inventory['quantity'] < 100]
            if not low_stock.empty:
                st.warning(f"⚠️ {len(low_stock)} items with low stock!")
                st.dataframe(low_stock[['item_name', 'quantity']], use_container_width=True)
    
    with tab2:
        with st.form("add_item"):
            item_name = st.text_input("Item Name*")
            category = st.selectbox("Category", ["Medicine", "Equipment", "Supplies", "Surgical"])
            quantity = st.number_input("Quantity", 0, 10000, 100)
            unit_price = st.number_input("Unit Price (Rs.)", 0, 100000, 50)
            supplier = st.text_input("Supplier")
            
            if st.form_submit_button("Add Item"):
                if item_name:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO inventory (item_name, category, quantity, unit_price, supplier, last_updated) VALUES (?, ?, ?, ?, ?, ?)",
                             (item_name, category, quantity, unit_price, supplier, datetime.now().strftime('%Y-%m-%d')))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Item {item_name} added!")
                    st.rerun()
                else:
                    st.error("Item name is required!")
    
    with tab3:
        conn = sqlite3.connect(DB_NAME)
        items = pd.read_sql("SELECT item_id, item_name, quantity FROM inventory", conn)
        conn.close()
        
        if not items.empty:
            item_id = st.selectbox("Select Item", items['item_id'].tolist(),
                                  format_func=lambda x: f"{items[items['item_id']==x]['item_name'].values[0]} (Current: {items[items['item_id']==x]['quantity'].values[0]})")
            
            col1, col2 = st.columns(2)
            with col1:
                add_qty = st.number_input("Add Quantity", 0, 10000, 0)
                if st.button("➕ Add Stock"):
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("UPDATE inventory SET quantity = quantity + ?, last_updated = ? WHERE item_id = ?",
                             (add_qty, datetime.now().strftime('%Y-%m-%d'), item_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ Stock added!")
                    st.rerun()
            
            with col2:
                remove_qty = st.number_input("Remove Quantity", 0, 10000, 0)
                if st.button("➖ Remove Stock"):
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("UPDATE inventory SET quantity = quantity - ?, last_updated = ? WHERE item_id = ?",
                             (remove_qty, datetime.now().strftime('%Y-%m-%d'), item_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ Stock removed!")
                    st.rerun()

elif page == "🛏️ Bed Management":
    st.header("🛏️ Bed Management")
    
    tab1, tab2, tab3 = st.tabs(["📊 View Beds", "➕ Add Bed", "🔄 Update Status"])
    
    with tab1:
        conn = sqlite3.connect(DB_NAME)
        beds = pd.read_sql("""
            SELECT b.bed_id, b.bed_number, b.ward_type, b.status, 
                   p.name as patient_name, b.admission_date
            FROM beds b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            ORDER BY b.bed_number
        """, conn)
        conn.close()
        st.dataframe(beds, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        available = len(beds[beds['status']=='Available'])
        occupied = len(beds[beds['status']=='Occupied'])
        col1.metric("✅ Available", available)
        col2.metric("🛌 Occupied", occupied)
        col3.metric("📊 Occupancy Rate", f"{(occupied/len(beds)*100):.1f}%" if len(beds) > 0 else "0%")
    
    with tab2:
        with st.form("add_bed"):
            bed_number = st.text_input("Bed Number*")
            ward_type = st.selectbox("Ward Type", ["General", "ICU", "Private", "Emergency", "Pediatric"])
            
            if st.form_submit_button("Add Bed"):
                if bed_number:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO beds (bed_number, ward_type, status, patient_id, admission_date) VALUES (?, ?, ?, ?, ?)",
                             (bed_number, ward_type, 'Available', None, None))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Bed {bed_number} added!")
                    st.rerun()
                else:
                    st.error("Bed number is required!")
    
    with tab3:
        conn = sqlite3.connect(DB_NAME)
        beds = pd.read_sql("SELECT bed_id, bed_number, status FROM beds", conn)
        patients = pd.read_sql("SELECT patient_id, name FROM patients", conn)
        conn.close()
        
        if not beds.empty:
            bed_id = st.selectbox("Select Bed", beds['bed_id'].tolist(),
                                 format_func=lambda x: f"{beds[beds['bed_id']==x]['bed_number'].values[0]} - {beds[beds['bed_id']==x]['status'].values[0]}")
            
            action = st.radio("Action", ["Admit Patient", "Discharge Patient"])
            
            if action == "Admit Patient":
                patient = st.selectbox("Patient", patients['patient_id'].tolist(),
                                      format_func=lambda x: patients[patients['patient_id']==x]['name'].values[0])
                if st.button("🛌 Admit"):
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("UPDATE beds SET status='Occupied', patient_id=?, admission_date=? WHERE bed_id=?",
                             (patient, datetime.now().strftime('%Y-%m-%d'), bed_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ Patient admitted!")
                    st.rerun()
            else:
                if st.button("🚪 Discharge"):
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("UPDATE beds SET status='Available', patient_id=NULL, admission_date=NULL WHERE bed_id=?", (bed_id,))
                    conn.commit()
                    conn.close()
                    st.success("✅ Patient discharged!")
                    st.rerun()

elif page == "🔬 Lab Tests":
    st.header("🔬 Laboratory Tests")
    
    tab1, tab2, tab3 = st.tabs(["📊 View Tests", "➕ Order Test", "📝 Update Results"])
    
    with tab1:
        conn = sqlite3.connect(DB_NAME)
        tests = pd.read_sql("""
            SELECT l.test_id, p.name as patient_name, l.test_name, l.test_date, 
                   l.result, l.status, l.cost
            FROM lab_tests l
            JOIN patients p ON l.patient_id = p.patient_id
            ORDER BY l.test_date DESC
        """, conn)
        conn.close()
        st.dataframe(tests, use_container_width=True)
        
        if not tests.empty:
            total_revenue = tests[tests['status']=='Completed']['cost'].sum()
            st.metric("💰 Lab Revenue", f"Rs. {total_revenue:,.0f}")
    
    with tab2:
        with st.form("order_test"):
            conn = sqlite3.connect(DB_NAME)
            patients = pd.read_sql("SELECT patient_id, name FROM patients", conn)
            conn.close()
            
            patient = st.selectbox("Patient*", patients['patient_id'].tolist(),
                                  format_func=lambda x: patients[patients['patient_id']==x]['name'].values[0])
            test_name = st.selectbox("Test Type", ["Blood Test", "X-Ray", "MRI Scan", "CT Scan", "Ultrasound", "ECG", "Urine Test"])
            cost = st.number_input("Cost (Rs.)", 0, 50000, 1500)
            
            if st.form_submit_button("Order Test"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO lab_tests (patient_id, test_name, test_date, result, status, cost) VALUES (?, ?, ?, ?, ?, ?)",
                         (patient, test_name, datetime.now().strftime('%Y-%m-%d'), None, 'Scheduled', cost))
                conn.commit()
                conn.close()
                st.success(f"✅ {test_name} ordered!")
                st.rerun()
    
    with tab3:
        conn = sqlite3.connect(DB_NAME)
        pending_tests = pd.read_sql("""
            SELECT l.test_id, p.name, l.test_name, l.status
            FROM lab_tests l
            JOIN patients p ON l.patient_id = p.patient_id
            WHERE l.status != 'Completed'
        """, conn)
        conn.close()
        
        if not pending_tests.empty:
            test_id = st.selectbox("Select Test", pending_tests['test_id'].tolist(),
                                  format_func=lambda x: f"{pending_tests[pending_tests['test_id']==x]['test_name'].values[0]} - {pending_tests[pending_tests['test_id']==x]['name'].values[0]}")
            
            result = st.text_area("Test Result")
            status = st.selectbox("Status", ["In Progress", "Completed"])
            
            if st.button("📝 Update"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("UPDATE lab_tests SET result=?, status=? WHERE test_id=?", (result, status, test_id))
                conn.commit()
                conn.close()
                st.success("✅ Test updated!")
                st.rerun()
        else:
            st.info("No pending tests")

elif page == "💊 Pharmacy":
    st.header("💊 Pharmacy Management")
    
    tab1, tab2 = st.tabs(["📊 View Prescriptions", "➕ Issue Medicine"])
    
    with tab1:
        conn = sqlite3.connect(DB_NAME)
        prescriptions = pd.read_sql("""
            SELECT ph.prescription_id, p.name as patient_name, d.name as doctor_name,
                   ph.medicine_name, ph.dosage, ph.quantity, ph.price, ph.issue_date
            FROM pharmacy ph
            JOIN patients p ON ph.patient_id = p.patient_id
            JOIN doctors d ON ph.doctor_id = d.doctor_id
            ORDER BY ph.issue_date DESC
        """, conn)
        conn.close()
        st.dataframe(prescriptions, use_container_width=True)
        
        if not prescriptions.empty:
            total_sales = prescriptions['price'].sum()
            st.metric("💰 Pharmacy Revenue", f"Rs. {total_sales:,.0f}")
    
    with tab2:
        with st.form("issue_medicine"):
            conn = sqlite3.connect(DB_NAME)
            patients = pd.read_sql("SELECT patient_id, name FROM patients", conn)
            doctors = pd.read_sql("SELECT doctor_id, name FROM doctors", conn)
            conn.close()
            
            patient = st.selectbox("Patient*", patients['patient_id'].tolist(),
                                  format_func=lambda x: patients[patients['patient_id']==x]['name'].values[0])
            doctor = st.selectbox("Doctor*", doctors['doctor_id'].tolist(),
                                 format_func=lambda x: doctors[doctors['doctor_id']==x]['name'].values[0])
            medicine = st.text_input("Medicine Name*")
            dosage = st.text_input("Dosage (e.g., 500mg)")
            quantity = st.number_input("Quantity", 1, 1000, 10)
            price = st.number_input("Price (Rs.)", 0, 100000, 100)
            
            if st.form_submit_button("Issue Medicine"):
                if medicine:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO pharmacy (patient_id, doctor_id, medicine_name, dosage, quantity, price, issue_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (patient, doctor, medicine, dosage, quantity, price, datetime.now().strftime('%Y-%m-%d')))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ {medicine} issued!")
                    st.rerun()
                else:
                    st.error("Medicine name is required!")

elif page == "🚑 Ambulance":
    st.header("🚑 Ambulance Service")
    
    tab1, tab2, tab3 = st.tabs(["📊 View Ambulances", "➕ Add Ambulance", "📞 Request Service"])
    
    with tab1:
        conn = sqlite3.connect(DB_NAME)
        ambulances = pd.read_sql("""
            SELECT a.ambulance_id, a.vehicle_number, a.driver_name, a.status,
                   p.name as patient_name, a.pickup_location, a.destination, a.request_time
            FROM ambulance a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
        """, conn)
        conn.close()
        st.dataframe(ambulances, use_container_width=True)
        
        col1, col2 = st.columns(2)
        available = len(ambulances[ambulances['status']=='Available'])
        on_duty = len(ambulances[ambulances['status']=='On Duty'])
        col1.metric("✅ Available", available)
        col2.metric("🚑 On Duty", on_duty)
    
    with tab2:
        with st.form("add_ambulance"):
            vehicle_number = st.text_input("Vehicle Number*")
            driver_name = st.text_input("Driver Name*")
            
            if st.form_submit_button("Add Ambulance"):
                if vehicle_number and driver_name:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO ambulance (vehicle_number, driver_name, status, patient_id, pickup_location, destination, request_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (vehicle_number, driver_name, 'Available', None, None, None, None))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Ambulance {vehicle_number} added!")
                    st.rerun()
                else:
                    st.error("All fields are required!")
    
    with tab3:
        conn = sqlite3.connect(DB_NAME)
        available_amb = pd.read_sql("SELECT ambulance_id, vehicle_number FROM ambulance WHERE status='Available'", conn)
        patients = pd.read_sql("SELECT patient_id, name FROM patients", conn)
        conn.close()
        
        if not available_amb.empty:
            with st.form("request_ambulance"):
                ambulance = st.selectbox("Select Ambulance", available_amb['ambulance_id'].tolist(),
                                        format_func=lambda x: available_amb[available_amb['ambulance_id']==x]['vehicle_number'].values[0])
                patient = st.selectbox("Patient", patients['patient_id'].tolist(),
                                      format_func=lambda x: patients[patients['patient_id']==x]['name'].values[0])
                pickup = st.text_input("Pickup Location*")
                destination = st.text_input("Destination*")
                
                if st.form_submit_button("📞 Request"):
                    if pickup and destination:
                        conn = sqlite3.connect(DB_NAME)
                        c = conn.cursor()
                        c.execute("UPDATE ambulance SET status='On Duty', patient_id=?, pickup_location=?, destination=?, request_time=? WHERE ambulance_id=?",
                                 (patient, pickup, destination, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ambulance))
                        conn.commit()
                        conn.close()
                        st.success("✅ Ambulance dispatched!")
                        st.rerun()
                    else:
                        st.error("All fields are required!")
        else:
            st.warning("No ambulances available")

elif page == "🩸 Blood Bank":
    st.header("🩸 Blood Bank Management")
    
    tab1, tab2 = st.tabs(["📊 View Stock", "➕ Add Donation"])
    
    with tab1:
        conn = sqlite3.connect(DB_NAME)
        blood_stock = pd.read_sql("SELECT * FROM blood_bank ORDER BY blood_group", conn)
        conn.close()
        st.dataframe(blood_stock, use_container_width=True)
        
        st.subheader("📊 Blood Group Availability")
        if not blood_stock.empty:
            fig = px.bar(blood_stock, x='blood_group', y='units', title='Blood Units by Group', color='units')
            st.plotly_chart(fig, use_container_width=True)
            
            low_stock = blood_stock[blood_stock['units'] < 10]
            if not low_stock.empty:
                st.warning(f"⚠️ Low stock alert for: {', '.join(low_stock['blood_group'].tolist())}")
    
    with tab2:
        with st.form("add_donation"):
            blood_group = st.selectbox("Blood Group*", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            units = st.number_input("Units", 1, 50, 1)
            donor_name = st.text_input("Donor Name*")
            
            if st.form_submit_button("Add Donation"):
                if donor_name:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    donation_date = datetime.now().strftime('%Y-%m-%d')
                    expiry_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
                    c.execute("INSERT INTO blood_bank (blood_group, units, donor_name, donation_date, expiry_date) VALUES (?, ?, ?, ?, ?)",
                             (blood_group, units, donor_name, donation_date, expiry_date))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ {units} unit(s) of {blood_group} added!")
                    st.rerun()
                else:
                    st.error("Donor name is required!")

st.sidebar.divider()
st.sidebar.info("🏥 Hospital Management System v3.0 Enterprise")
st.sidebar.success(f"📅 {datetime.now().strftime('%d %B %Y')}")
st.sidebar.metric("🕒 Time", datetime.now().strftime('%I:%M %p'))
