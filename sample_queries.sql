-- Hospital Management System - Sample SQL Queries
-- Common queries for hospital operations

-- ========================================
-- PATIENT QUERIES
-- ========================================

-- 1. Get all patients with their basic info
SELECT patient_id, name, age, gender, phone, blood_group, registration_date 
FROM patients 
ORDER BY registration_date DESC;

-- 2. Find patients by age group
SELECT name, age, gender, phone 
FROM patients 
WHERE age BETWEEN 18 AND 65 
ORDER BY age;

-- 3. Search patients by name (partial match)
SELECT * FROM patients 
WHERE name LIKE '%Ahmed%' 
ORDER BY name;

-- 4. Get patients with specific blood group
SELECT name, age, phone, address 
FROM patients 
WHERE blood_group = 'O+';

-- 5. Count patients by gender
SELECT gender, COUNT(*) as patient_count 
FROM patients 
GROUP BY gender;

-- ========================================
-- DOCTOR QUERIES
-- ========================================

-- 6. Get all doctors with department info
SELECT d.name, d.specialization, d.experience_years, d.consultation_fee, dept.dept_name
FROM doctors d
LEFT JOIN departments dept ON d.dept_id = dept.dept_id
ORDER BY d.experience_years DESC;

-- 7. Find doctors by specialization
SELECT name, phone, email, experience_years, consultation_fee
FROM doctors 
WHERE specialization = 'Cardiologist';

-- 8. Get highest paid doctors
SELECT name, specialization, consultation_fee
FROM doctors 
ORDER BY consultation_fee DESC 
LIMIT 5;

-- 9. Average consultation fee by specialization
SELECT specialization, AVG(consultation_fee) as avg_fee, COUNT(*) as doctor_count
FROM doctors 
GROUP BY specialization 
ORDER BY avg_fee DESC;

-- ========================================
-- APPOINTMENT QUERIES
-- ========================================

-- 10. Today's appointments
SELECT p.name as patient_name, d.name as doctor_name, 
       a.appointment_time, a.reason, a.status
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id
WHERE a.appointment_date = DATE('now')
ORDER BY a.appointment_time;

-- 11. Upcoming appointments (next 7 days)
SELECT p.name as patient_name, d.name as doctor_name, 
       a.appointment_date, a.appointment_time, a.status
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id
WHERE a.appointment_date BETWEEN DATE('now') AND DATE('now', '+7 days')
ORDER BY a.appointment_date, a.appointment_time;

-- 12. Cancelled appointments this month
SELECT p.name as patient_name, d.name as doctor_name, 
       a.appointment_date, a.reason
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id
WHERE a.status = 'Cancelled' 
AND strftime('%Y-%m', a.appointment_date) = strftime('%Y-%m', 'now');

-- 13. Doctor with most appointments
SELECT d.name, d.specialization, COUNT(a.appointment_id) as appointment_count
FROM doctors d
LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY d.doctor_id, d.name, d.specialization
ORDER BY appointment_count DESC
LIMIT 1;

-- 14. Appointments by status
SELECT status, COUNT(*) as count
FROM appointments 
GROUP BY status;

-- ========================================
-- MEDICAL RECORDS QUERIES
-- ========================================

-- 15. Patient medical history
SELECT mr.visit_date, d.name as doctor_name, mr.diagnosis, 
       mr.prescription, mr.cost
FROM medical_records mr
JOIN doctors d ON mr.doctor_id = d.doctor_id
WHERE mr.patient_id = 1
ORDER BY mr.visit_date DESC;

-- 16. Most common diagnoses
SELECT diagnosis, COUNT(*) as frequency
FROM medical_records 
GROUP BY diagnosis 
ORDER BY frequency DESC 
LIMIT 10;

-- 17. Revenue by month
SELECT strftime('%Y-%m', visit_date) as month, 
       SUM(cost) as total_revenue,
       COUNT(*) as total_visits
FROM medical_records 
WHERE cost IS NOT NULL
GROUP BY strftime('%Y-%m', visit_date)
ORDER BY month DESC;

-- 18. High-cost treatments
SELECT p.name as patient_name, d.name as doctor_name, 
       mr.diagnosis, mr.cost, mr.visit_date
FROM medical_records mr
JOIN patients p ON mr.patient_id = p.patient_id
JOIN doctors d ON mr.doctor_id = d.doctor_id
WHERE mr.cost > 5000
ORDER BY mr.cost DESC;

-- ========================================
-- DEPARTMENT QUERIES
-- ========================================

-- 19. Department performance
SELECT dept.dept_name, 
       COUNT(DISTINCT d.doctor_id) as total_doctors,
       COUNT(a.appointment_id) as total_appointments,
       AVG(d.consultation_fee) as avg_fee
FROM departments dept
LEFT JOIN doctors d ON dept.dept_id = d.dept_id
LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY dept.dept_id, dept.dept_name;

-- 20. Busiest departments
SELECT dept.dept_name, COUNT(a.appointment_id) as appointment_count
FROM departments dept
JOIN doctors d ON dept.dept_id = d.dept_id
JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY dept.dept_name
ORDER BY appointment_count DESC;

-- ========================================
-- COMPLEX ANALYTICAL QUERIES
-- ========================================

-- 21. Patient age distribution
SELECT 
    CASE 
        WHEN age < 18 THEN 'Child (0-17)'
        WHEN age BETWEEN 18 AND 35 THEN 'Young Adult (18-35)'
        WHEN age BETWEEN 36 AND 55 THEN 'Middle Age (36-55)'
        WHEN age > 55 THEN 'Senior (55+)'
    END as age_group,
    COUNT(*) as patient_count
FROM patients 
GROUP BY age_group;

-- 22. Doctor workload analysis
SELECT d.name, d.specialization,
       COUNT(a.appointment_id) as total_appointments,
       COUNT(CASE WHEN a.appointment_date >= DATE('now', '-30 days') THEN 1 END) as recent_appointments,
       AVG(CASE WHEN mr.cost IS NOT NULL THEN mr.cost END) as avg_treatment_cost
FROM doctors d
LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
LEFT JOIN medical_records mr ON d.doctor_id = mr.doctor_id
GROUP BY d.doctor_id, d.name, d.specialization
ORDER BY total_appointments DESC;

-- 23. Emergency cases analysis
SELECT DATE(a.appointment_date) as date,
       COUNT(*) as emergency_cases,
       AVG(mr.cost) as avg_cost
FROM appointments a
LEFT JOIN medical_records mr ON a.appointment_id = mr.record_id
WHERE a.reason LIKE '%emergency%' OR a.reason LIKE '%Emergency%'
GROUP BY DATE(a.appointment_date)
ORDER BY date DESC;

-- 24. Patient loyalty analysis
SELECT p.name, p.registration_date,
       COUNT(a.appointment_id) as total_visits,
       SUM(mr.cost) as total_spent,
       MAX(a.appointment_date) as last_visit
FROM patients p
LEFT JOIN appointments a ON p.patient_id = a.patient_id
LEFT JOIN medical_records mr ON p.patient_id = mr.patient_id
GROUP BY p.patient_id, p.name, p.registration_date
HAVING COUNT(a.appointment_id) > 1
ORDER BY total_visits DESC;

-- 25. Monthly growth analysis
SELECT 
    strftime('%Y-%m', registration_date) as month,
    COUNT(*) as new_patients,
    LAG(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', registration_date)) as prev_month,
    ROUND(
        (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', registration_date))) * 100.0 / 
        LAG(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', registration_date)), 2
    ) as growth_percentage
FROM patients 
GROUP BY strftime('%Y-%m', registration_date)
ORDER BY month DESC;