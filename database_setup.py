import sqlite3
import datetime

def create_hospital_database():
    """Create and populate hospital database with sample data"""
    conn = sqlite3.connect('hospital_new.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS appointments')
    cursor.execute('DROP TABLE IF EXISTS medical_records')
    cursor.execute('DROP TABLE IF EXISTS patients')
    cursor.execute('DROP TABLE IF EXISTS doctors')
    cursor.execute('DROP TABLE IF EXISTS departments')
    
    # Create departments table
    cursor.execute('''
        CREATE TABLE departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT NOT NULL,
            head_doctor TEXT,
            location TEXT,
            phone TEXT
        )
    ''')
    
    # Create doctors table
    cursor.execute('''
        CREATE TABLE doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            dept_id INTEGER,
            phone TEXT,
            email TEXT,
            experience_years INTEGER,
            consultation_fee REAL,
            FOREIGN KEY (dept_id) REFERENCES departments (dept_id)
        )
    ''')
    
    # Create patients table
    cursor.execute('''
        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            emergency_contact TEXT,
            blood_group TEXT,
            registration_date DATE
        )
    ''')
    
    # Create appointments table
    cursor.execute('''
        CREATE TABLE appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            appointment_date DATE,
            appointment_time TEXT,
            status TEXT DEFAULT 'Scheduled',
            reason TEXT,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        )
    ''')
    
    # Create medical records table
    cursor.execute('''
        CREATE TABLE medical_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            visit_date DATE,
            diagnosis TEXT,
            prescription TEXT,
            treatment TEXT,
            follow_up_date DATE,
            cost REAL,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        )
    ''')
    
    # Insert sample departments
    departments_data = [
        ('Cardiology', 'Dr. Ahmed Khan', 'Block A, Floor 2', '021-1234567'),
        ('Neurology', 'Dr. Sarah Ali', 'Block B, Floor 3', '021-2345678'),
        ('Orthopedics', 'Dr. Hassan Sheikh', 'Block C, Floor 1', '021-3456789'),
        ('Pediatrics', 'Dr. Fatima Malik', 'Block A, Floor 1', '021-4567890'),
        ('Emergency', 'Dr. Omar Siddiqui', 'Ground Floor', '021-5678901')
    ]
    
    cursor.executemany('INSERT INTO departments (dept_name, head_doctor, location, phone) VALUES (?, ?, ?, ?)', departments_data)
    
    # Insert sample doctors
    doctors_data = [
        ('Dr. Ahmed Khan', 'Cardiologist', 1, '0300-1234567', 'ahmed.khan@hospital.com', 15, 3000),
        ('Dr. Sarah Ali', 'Neurologist', 2, '0300-2345678', 'sarah.ali@hospital.com', 12, 3500),
        ('Dr. Hassan Sheikh', 'Orthopedic Surgeon', 3, '0300-3456789', 'hassan.sheikh@hospital.com', 18, 4000),
        ('Dr. Fatima Malik', 'Pediatrician', 4, '0300-4567890', 'fatima.malik@hospital.com', 10, 2500),
        ('Dr. Omar Siddiqui', 'Emergency Medicine', 5, '0300-5678901', 'omar.siddiqui@hospital.com', 8, 2000),
        ('Dr. Zainab Qureshi', 'Cardiologist', 1, '0300-6789012', 'zainab.qureshi@hospital.com', 7, 2800),
        ('Dr. Ali Raza', 'Neurologist', 2, '0300-7890123', 'ali.raza@hospital.com', 5, 3200)
    ]
    
    cursor.executemany('INSERT INTO doctors (name, specialization, dept_id, phone, email, experience_years, consultation_fee) VALUES (?, ?, ?, ?, ?, ?, ?)', doctors_data)
    
    # Insert sample patients
    patients_data = [
        ('Muhammad Asif', 45, 'Male', '0301-1111111', 'asif@email.com', 'Karachi, Pakistan', '0302-2222222', 'B+', '2024-01-15'),
        ('Ayesha Khan', 32, 'Female', '0301-3333333', 'ayesha@email.com', 'Lahore, Pakistan', '0302-4444444', 'A+', '2024-01-20'),
        ('Bilal Ahmed', 28, 'Male', '0301-5555555', 'bilal@email.com', 'Islamabad, Pakistan', '0302-6666666', 'O+', '2024-02-01'),
        ('Sana Malik', 35, 'Female', '0301-7777777', 'sana@email.com', 'Faisalabad, Pakistan', '0302-8888888', 'AB+', '2024-02-10'),
        ('Ahmed Ali', 50, 'Male', '0301-9999999', 'ahmed@email.com', 'Peshawar, Pakistan', '0302-0000000', 'B-', '2024-02-15')
    ]
    
    cursor.executemany('INSERT INTO patients (name, age, gender, phone, email, address, emergency_contact, blood_group, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', patients_data)
    
    # Insert sample appointments
    appointments_data = [
        (1, 1, '2024-12-20', '10:00 AM', 'Scheduled', 'Chest pain', 'Regular checkup'),
        (2, 2, '2024-12-21', '2:00 PM', 'Completed', 'Headache', 'MRI recommended'),
        (3, 3, '2024-12-22', '11:00 AM', 'Scheduled', 'Knee pain', 'X-ray required'),
        (4, 4, '2024-12-23', '9:00 AM', 'Scheduled', 'Child fever', 'Routine checkup'),
        (5, 5, '2024-12-19', '8:00 PM', 'Completed', 'Emergency', 'Accident case')
    ]
    
    cursor.executemany('INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, reason, notes) VALUES (?, ?, ?, ?, ?, ?, ?)', appointments_data)
    
    # Insert sample medical records
    medical_records_data = [
        (1, 1, '2024-12-15', 'Hypertension', 'Amlodipine 5mg daily', 'Lifestyle changes recommended', '2025-01-15', 3000),
        (2, 2, '2024-12-10', 'Migraine', 'Sumatriptan as needed', 'Stress management', '2024-12-25', 3500),
        (5, 5, '2024-12-19', 'Fracture - Right arm', 'Cast applied', 'Surgery not required', '2025-01-02', 15000)
    ]
    
    cursor.executemany('INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, prescription, treatment, follow_up_date, cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', medical_records_data)
    
    conn.commit()
    conn.close()
    print("Hospital database created successfully with sample data!")

if __name__ == "__main__":
    create_hospital_database()