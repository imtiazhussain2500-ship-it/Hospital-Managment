-- Hospital Management System Database Schema
-- SQLite Database Structure

-- Create Departments Table
CREATE TABLE IF NOT EXISTS departments (
    dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dept_name TEXT NOT NULL UNIQUE,
    head_doctor TEXT,
    location TEXT,
    phone TEXT,
    budget REAL DEFAULT 0,
    created_date DATE DEFAULT CURRENT_DATE
);

-- Create Doctors Table
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    dept_id INTEGER,
    phone TEXT UNIQUE,
    email TEXT UNIQUE,
    experience_years INTEGER CHECK(experience_years >= 0),
    consultation_fee REAL CHECK(consultation_fee > 0),
    qualification TEXT,
    license_number TEXT UNIQUE,
    hire_date DATE DEFAULT CURRENT_DATE,
    status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Inactive', 'On Leave')),
    FOREIGN KEY (dept_id) REFERENCES departments (dept_id) ON DELETE SET NULL
);

-- Create Patients Table
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER CHECK(age > 0 AND age < 150),
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    phone TEXT,
    email TEXT,
    address TEXT,
    emergency_contact TEXT,
    blood_group TEXT CHECK(blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    registration_date DATE DEFAULT CURRENT_DATE,
    insurance_id TEXT,
    allergies TEXT,
    chronic_conditions TEXT
);

-- Create Appointments Table
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TEXT NOT NULL,
    status TEXT DEFAULT 'Scheduled' CHECK(status IN ('Scheduled', 'Completed', 'Cancelled', 'No Show')),
    reason TEXT,
    notes TEXT,
    priority TEXT DEFAULT 'Normal' CHECK(priority IN ('Emergency', 'Urgent', 'Normal')),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id) ON DELETE CASCADE
);

-- Create Medical Records Table
CREATE TABLE IF NOT EXISTS medical_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    visit_date DATE NOT NULL,
    diagnosis TEXT NOT NULL,
    prescription TEXT,
    treatment TEXT,
    follow_up_date DATE,
    cost REAL CHECK(cost >= 0),
    symptoms TEXT,
    vital_signs TEXT,
    lab_results TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id) ON DELETE CASCADE
);

-- Create Staff Table
CREATE TABLE IF NOT EXISTS staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    dept_id INTEGER,
    phone TEXT,
    email TEXT UNIQUE,
    salary REAL,
    hire_date DATE DEFAULT CURRENT_DATE,
    shift TEXT CHECK(shift IN ('Morning', 'Evening', 'Night')),
    FOREIGN KEY (dept_id) REFERENCES departments (dept_id) ON DELETE SET NULL
);

-- Create Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER DEFAULT 0,
    unit_price REAL,
    supplier TEXT,
    expiry_date DATE,
    minimum_stock INTEGER DEFAULT 10,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create Bills Table
CREATE TABLE IF NOT EXISTS bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    appointment_id INTEGER,
    total_amount REAL NOT NULL,
    paid_amount REAL DEFAULT 0,
    payment_status TEXT DEFAULT 'Pending' CHECK(payment_status IN ('Pending', 'Partial', 'Paid')),
    payment_method TEXT CHECK(payment_method IN ('Cash', 'Card', 'Insurance', 'Online')),
    bill_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id) ON DELETE SET NULL
);

-- Create Indexes for Better Performance
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_date ON medical_records(visit_date);
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name);
CREATE INDEX IF NOT EXISTS idx_doctors_specialization ON doctors(specialization);

-- Create Views for Common Queries
CREATE VIEW IF NOT EXISTS doctor_appointments AS
SELECT 
    d.name as doctor_name,
    d.specialization,
    dept.dept_name,
    COUNT(a.appointment_id) as total_appointments,
    COUNT(CASE WHEN a.status = 'Completed' THEN 1 END) as completed_appointments,
    COUNT(CASE WHEN a.status = 'Scheduled' THEN 1 END) as scheduled_appointments
FROM doctors d
LEFT JOIN departments dept ON d.dept_id = dept.dept_id
LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY d.doctor_id, d.name, d.specialization, dept.dept_name;

CREATE VIEW IF NOT EXISTS patient_summary AS
SELECT 
    p.patient_id,
    p.name,
    p.age,
    p.gender,
    p.blood_group,
    COUNT(a.appointment_id) as total_appointments,
    COUNT(mr.record_id) as total_visits,
    COALESCE(SUM(mr.cost), 0) as total_spent
FROM patients p
LEFT JOIN appointments a ON p.patient_id = a.patient_id
LEFT JOIN medical_records mr ON p.patient_id = mr.patient_id
GROUP BY p.patient_id, p.name, p.age, p.gender, p.blood_group;

CREATE VIEW IF NOT EXISTS department_stats AS
SELECT 
    d.dept_name,
    d.head_doctor,
    d.location,
    COUNT(doc.doctor_id) as total_doctors,
    COUNT(a.appointment_id) as total_appointments,
    COALESCE(AVG(doc.consultation_fee), 0) as avg_consultation_fee
FROM departments d
LEFT JOIN doctors doc ON d.dept_id = doc.dept_id
LEFT JOIN appointments a ON doc.doctor_id = a.doctor_id
GROUP BY d.dept_id, d.dept_name, d.head_doctor, d.location;

-- Triggers for Data Integrity
CREATE TRIGGER IF NOT EXISTS update_bill_status
AFTER UPDATE OF paid_amount ON bills
BEGIN
    UPDATE bills 
    SET payment_status = CASE 
        WHEN NEW.paid_amount >= NEW.total_amount THEN 'Paid'
        WHEN NEW.paid_amount > 0 THEN 'Partial'
        ELSE 'Pending'
    END
    WHERE bill_id = NEW.bill_id;
END;

CREATE TRIGGER IF NOT EXISTS update_inventory_timestamp
AFTER UPDATE ON inventory
BEGIN
    UPDATE inventory 
    SET last_updated = CURRENT_TIMESTAMP 
    WHERE item_id = NEW.item_id;
END;