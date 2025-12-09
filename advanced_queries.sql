-- Advanced SQL Queries for Hospital Management System
-- Complex analytical and reporting queries

-- ========================================
-- REVENUE & FINANCIAL ANALYSIS
-- ========================================

-- 1. Monthly Revenue Trend with Growth Rate
WITH monthly_revenue AS (
    SELECT 
        strftime('%Y-%m', visit_date) as month,
        SUM(cost) as revenue,
        COUNT(*) as visits
    FROM medical_records 
    WHERE cost IS NOT NULL
    GROUP BY strftime('%Y-%m', visit_date)
)
SELECT 
    month,
    revenue,
    visits,
    LAG(revenue) OVER (ORDER BY month) as prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 / 
        LAG(revenue) OVER (ORDER BY month), 2
    ) as growth_rate_percent
FROM monthly_revenue
ORDER BY month DESC;

-- 2. Top Revenue Generating Doctors
SELECT 
    d.name,
    d.specialization,
    COUNT(mr.record_id) as total_treatments,
    SUM(mr.cost) as total_revenue,
    AVG(mr.cost) as avg_treatment_cost,
    RANK() OVER (ORDER BY SUM(mr.cost) DESC) as revenue_rank
FROM doctors d
JOIN medical_records mr ON d.doctor_id = mr.doctor_id
WHERE mr.cost IS NOT NULL
GROUP BY d.doctor_id, d.name, d.specialization
ORDER BY total_revenue DESC
LIMIT 10;

-- 3. Department Profitability Analysis
SELECT 
    dept.dept_name,
    COUNT(DISTINCT d.doctor_id) as doctors_count,
    COUNT(mr.record_id) as total_treatments,
    SUM(mr.cost) as total_revenue,
    AVG(mr.cost) as avg_treatment_cost,
    SUM(d.consultation_fee * 
        (SELECT COUNT(*) FROM appointments a WHERE a.doctor_id = d.doctor_id AND a.status = 'Completed')
    ) as consultation_revenue
FROM departments dept
LEFT JOIN doctors d ON dept.dept_id = d.dept_id
LEFT JOIN medical_records mr ON d.doctor_id = mr.doctor_id
WHERE mr.cost IS NOT NULL
GROUP BY dept.dept_id, dept.dept_name
ORDER BY total_revenue DESC;

-- ========================================
-- PATIENT ANALYTICS
-- ========================================

-- 4. Patient Retention Analysis
WITH patient_visits AS (
    SELECT 
        p.patient_id,
        p.name,
        p.registration_date,
        COUNT(a.appointment_id) as total_visits,
        MIN(a.appointment_date) as first_visit,
        MAX(a.appointment_date) as last_visit,
        JULIANDAY('now') - JULIANDAY(MAX(a.appointment_date)) as days_since_last_visit
    FROM patients p
    LEFT JOIN appointments a ON p.patient_id = a.patient_id
    GROUP BY p.patient_id, p.name, p.registration_date
)
SELECT 
    CASE 
        WHEN days_since_last_visit <= 30 THEN 'Active (0-30 days)'
        WHEN days_since_last_visit <= 90 THEN 'Recent (31-90 days)'
        WHEN days_since_last_visit <= 180 THEN 'Inactive (91-180 days)'
        ELSE 'Lost (180+ days)'
    END as patient_status,
    COUNT(*) as patient_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM patients), 2) as percentage
FROM patient_visits
WHERE total_visits > 0
GROUP BY patient_status;

-- 5. High-Value Patients
SELECT 
    p.name,
    p.age,
    p.gender,
    COUNT(mr.record_id) as total_visits,
    SUM(mr.cost) as total_spent,
    AVG(mr.cost) as avg_per_visit,
    MAX(mr.visit_date) as last_visit_date
FROM patients p
JOIN medical_records mr ON p.patient_id = mr.patient_id
WHERE mr.cost IS NOT NULL
GROUP BY p.patient_id, p.name, p.age, p.gender
HAVING SUM(mr.cost) > 10000
ORDER BY total_spent DESC;

-- ========================================
-- OPERATIONAL EFFICIENCY
-- ========================================

-- 6. Doctor Utilization Rate
WITH doctor_capacity AS (
    SELECT 
        d.doctor_id,
        d.name,
        d.specialization,
        COUNT(a.appointment_id) as actual_appointments,
        -- Assuming 8 appointments per day, 22 working days per month
        22 * 8 as monthly_capacity,
        strftime('%Y-%m', a.appointment_date) as month
    FROM doctors d
    LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
    WHERE a.appointment_date >= DATE('now', '-3 months')
    GROUP BY d.doctor_id, d.name, d.specialization, strftime('%Y-%m', a.appointment_date)
)
SELECT 
    name,
    specialization,
    AVG(actual_appointments) as avg_monthly_appointments,
    monthly_capacity,
    ROUND(AVG(actual_appointments) * 100.0 / monthly_capacity, 2) as utilization_rate
FROM doctor_capacity
GROUP BY doctor_id, name, specialization, monthly_capacity
ORDER BY utilization_rate DESC;

-- 7. Appointment No-Show Analysis
SELECT 
    strftime('%Y-%m', appointment_date) as month,
    COUNT(*) as total_appointments,
    COUNT(CASE WHEN status = 'No Show' THEN 1 END) as no_shows,
    COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) as cancellations,
    ROUND(COUNT(CASE WHEN status = 'No Show' THEN 1 END) * 100.0 / COUNT(*), 2) as no_show_rate,
    ROUND(COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) * 100.0 / COUNT(*), 2) as cancellation_rate
FROM appointments
WHERE appointment_date >= DATE('now', '-12 months')
GROUP BY strftime('%Y-%m', appointment_date)
ORDER BY month DESC;

-- ========================================
-- MEDICAL INSIGHTS
-- ========================================

-- 8. Disease Pattern Analysis
WITH diagnosis_trends AS (
    SELECT 
        LOWER(TRIM(diagnosis)) as normalized_diagnosis,
        strftime('%Y-%m', visit_date) as month,
        COUNT(*) as case_count
    FROM medical_records
    WHERE diagnosis IS NOT NULL AND diagnosis != ''
    GROUP BY normalized_diagnosis, strftime('%Y-%m', visit_date)
)
SELECT 
    normalized_diagnosis,
    SUM(case_count) as total_cases,
    COUNT(DISTINCT month) as months_active,
    AVG(case_count) as avg_monthly_cases,
    MAX(case_count) as peak_monthly_cases
FROM diagnosis_trends
GROUP BY normalized_diagnosis
HAVING total_cases >= 5
ORDER BY total_cases DESC
LIMIT 15;

-- 9. Treatment Cost Analysis by Age Group
SELECT 
    CASE 
        WHEN p.age < 18 THEN 'Pediatric (0-17)'
        WHEN p.age BETWEEN 18 AND 35 THEN 'Young Adult (18-35)'
        WHEN p.age BETWEEN 36 AND 55 THEN 'Middle Age (36-55)'
        WHEN p.age BETWEEN 56 AND 70 THEN 'Senior (56-70)'
        WHEN p.age > 70 THEN 'Elderly (70+)'
    END as age_group,
    COUNT(mr.record_id) as total_treatments,
    AVG(mr.cost) as avg_cost,
    MIN(mr.cost) as min_cost,
    MAX(mr.cost) as max_cost,
    SUM(mr.cost) as total_cost
FROM patients p
JOIN medical_records mr ON p.patient_id = mr.patient_id
WHERE mr.cost IS NOT NULL
GROUP BY age_group
ORDER BY avg_cost DESC;

-- ========================================
-- PREDICTIVE ANALYTICS
-- ========================================

-- 10. Seasonal Appointment Patterns
SELECT 
    CASE strftime('%m', appointment_date)
        WHEN '01' THEN 'January'
        WHEN '02' THEN 'February'
        WHEN '03' THEN 'March'
        WHEN '04' THEN 'April'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'June'
        WHEN '07' THEN 'July'
        WHEN '08' THEN 'August'
        WHEN '09' THEN 'September'
        WHEN '10' THEN 'October'
        WHEN '11' THEN 'November'
        WHEN '12' THEN 'December'
    END as month_name,
    COUNT(*) as total_appointments,
    AVG(COUNT(*)) OVER () as yearly_average,
    ROUND((COUNT(*) - AVG(COUNT(*)) OVER ()) * 100.0 / AVG(COUNT(*)) OVER (), 2) as variance_from_avg
FROM appointments
GROUP BY strftime('%m', appointment_date)
ORDER BY strftime('%m', appointment_date);

-- 11. Patient Risk Stratification
WITH patient_metrics AS (
    SELECT 
        p.patient_id,
        p.name,
        p.age,
        COUNT(mr.record_id) as visit_frequency,
        AVG(mr.cost) as avg_treatment_cost,
        COUNT(DISTINCT mr.diagnosis) as unique_diagnoses,
        JULIANDAY('now') - JULIANDAY(MAX(mr.visit_date)) as days_since_last_visit
    FROM patients p
    LEFT JOIN medical_records mr ON p.patient_id = mr.patient_id
    GROUP BY p.patient_id, p.name, p.age
)
SELECT 
    name,
    age,
    visit_frequency,
    avg_treatment_cost,
    unique_diagnoses,
    days_since_last_visit,
    CASE 
        WHEN visit_frequency >= 5 AND avg_treatment_cost > 3000 THEN 'High Risk'
        WHEN visit_frequency >= 3 OR avg_treatment_cost > 2000 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_category
FROM patient_metrics
WHERE visit_frequency > 0
ORDER BY 
    CASE 
        WHEN visit_frequency >= 5 AND avg_treatment_cost > 3000 THEN 1
        WHEN visit_frequency >= 3 OR avg_treatment_cost > 2000 THEN 2
        ELSE 3
    END,
    visit_frequency DESC;

-- ========================================
-- PERFORMANCE BENCHMARKING
-- ========================================

-- 12. Department Comparison Dashboard
WITH dept_metrics AS (
    SELECT 
        dept.dept_name,
        COUNT(DISTINCT d.doctor_id) as doctor_count,
        COUNT(a.appointment_id) as total_appointments,
        COUNT(CASE WHEN a.status = 'Completed' THEN 1 END) as completed_appointments,
        AVG(d.consultation_fee) as avg_consultation_fee,
        SUM(mr.cost) as total_revenue
    FROM departments dept
    LEFT JOIN doctors d ON dept.dept_id = d.dept_id
    LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
    LEFT JOIN medical_records mr ON d.doctor_id = mr.doctor_id
    GROUP BY dept.dept_id, dept.dept_name
)
SELECT 
    dept_name,
    doctor_count,
    total_appointments,
    completed_appointments,
    ROUND(completed_appointments * 100.0 / NULLIF(total_appointments, 0), 2) as completion_rate,
    ROUND(avg_consultation_fee, 2) as avg_consultation_fee,
    COALESCE(total_revenue, 0) as total_revenue,
    ROUND(COALESCE(total_revenue, 0) / NULLIF(doctor_count, 0), 2) as revenue_per_doctor
FROM dept_metrics
ORDER BY total_revenue DESC;