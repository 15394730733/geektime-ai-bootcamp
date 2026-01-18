# Interview Database - Quick Reference Card

## 🚀 Quick Start

### Create Database
```bash
mysql -u root -p < create_interview_db.sql
```

### Connect to Database
```bash
mysql -u root -p interview_db
```

### Test with Python
```bash
python test_interview_db.py
```

---

## 📊 Essential Queries

### 1. Database Overview
```sql
-- Show all tables
SHOW TABLES;

-- Count records in each table
SELECT
    'candidates' as table_name, COUNT(*) as count FROM candidates
UNION ALL SELECT 'positions', COUNT(*) FROM positions
UNION ALL SELECT 'interviews', COUNT(*) FROM interviews
UNION ALL SELECT 'evaluations', COUNT(*) FROM interview_evaluations;
```

### 2. Candidates Pipeline
```sql
-- Candidate funnel
SELECT
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM candidates), 1) as percentage
FROM candidates
GROUP BY status
ORDER BY
    FIELD(status,
        'applied',
        'screening',
        'interviewing',
        'offered',
        'hired',
        'rejected',
        'withdrawn'
    );
```

### 3. Active Interviews Today
```sql
SELECT
    CONCAT(c.first_name, ' ', c.last_name) as candidate,
    p.position_title,
    s.stage_name,
    i.scheduled_date,
    i.location,
    i.meeting_url
FROM interviews i
JOIN job_applications ja ON i.application_id = ja.application_id
JOIN candidates c ON ja.candidate_id = c.candidate_id
JOIN positions p ON ja.position_id = p.position_id
JOIN interview_stages s ON i.stage_id = s.stage_id
WHERE DATE(i.scheduled_date) = CURDATE()
  AND i.status = 'scheduled'
ORDER BY i.scheduled_date;
```

### 4. Top Candidates (Hire Recommendations)
```sql
-- Candidates with strong hire recommendations
SELECT DISTINCT
    CONCAT(c.first_name, ' ', c.last_name) as candidate_name,
    c.email,
    c.phone,
    p.position_title,
    COUNT(ie.evaluation_id) as evaluation_count,
    ROUND(AVG(ie.overall_score), 2) as avg_score
FROM candidates c
JOIN job_applications ja ON c.candidate_id = ja.candidate_id
JOIN positions p ON ja.position_id = p.position_id
JOIN interviews i ON ja.application_id = i.application_id
JOIN interview_evaluations ie ON i.interview_id = ie.interview_id
WHERE ie.recommendation IN ('strong_hire', 'hire')
GROUP BY c.candidate_id, c.first_name, c.last_name, c.email, c.phone, p.position_title
HAVING evaluation_count >= 2
ORDER BY avg_score DESC;
```

### 5. Position Status
```sql
-- Open positions with applicants
SELECT
    p.position_title,
    d.department_name,
    p.salary_min,
    p.salary_max,
    (p.headcount - p.current_count) as openings,
    COUNT(DISTINCT ja.candidate_id) as applicants,
    SUM(CASE WHEN ja.status = 'interviewing' THEN 1 ELSE 0 END) as interviewing,
    SUM(CASE WHEN ja.status = 'offered' THEN 1 ELSE 0 END) as offered
FROM positions p
JOIN departments d ON p.department_id = d.department_id
LEFT JOIN job_applications ja ON p.position_id = ja.position_id
WHERE p.status = 'active'
GROUP BY p.position_id, p.position_title, d.department_name, p.salary_min, p.salary_max, p.headcount, p.current_count
HAVING openings > 0
ORDER BY openings DESC;
```

### 6. Interview Schedule (Next 7 Days)
```sql
SELECT
    DATE(i.scheduled_date) as interview_date,
    TIME(i.scheduled_date) as interview_time,
    CONCAT(c.first_name, ' ', c.last_name) as candidate,
    p.position_title,
    s.stage_name,
    i.duration_minutes,
    GROUP_CONCAT(CONCAT(e.first_name, ' ', e.last_name) SEPARATOR ', ') as interviewers
FROM interviews i
JOIN job_applications ja ON i.application_id = ja.application_id
JOIN candidates c ON ja.candidate_id = c.candidate_id
JOIN positions p ON ja.position_id = p.position_id
JOIN interview_stages s ON i.stage_id = s.stage_id
LEFT JOIN interview_participants ip ON i.interview_id = ip.interview_id
LEFT JOIN employees e ON ip.employee_id = e.employee_id
WHERE i.scheduled_date BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY)
  AND i.status = 'scheduled'
GROUP BY i.interview_id, DATE(i.scheduled_date), TIME(i.scheduled_date), c.first_name, c.last_name, p.position_title, s.stage_name, i.duration_minutes
ORDER BY i.scheduled_date;
```

### 7. Skills Gap Analysis
```sql
-- Candidates applied vs required skills
SELECT
    p.position_title,
    s.skill_name,
    ps.required_level,
    COUNT(DISTINCT ja.candidate_id) as total_applicants,
    COUNT(DISTINCT CASE WHEN cs.candidate_id IS NOT NULL THEN ja.candidate_id END) as with_skill,
    ROUND(COUNT(DISTINCT CASE WHEN cs.candidate_id IS NOT NULL THEN ja.candidate_id END) * 100.0 / COUNT(DISTINCT ja.candidate_id), 1) as coverage_percent
FROM positions p
JOIN position_skills ps ON p.position_id = ps.position_id
JOIN skills s ON ps.skill_id = s.skill_id
LEFT JOIN job_applications ja ON p.position_id = ja.position_id
LEFT JOIN candidate_skills cs ON ja.candidate_id = cs.candidate_id AND cs.skill_id = s.skill_id
WHERE p.status = 'active'
GROUP BY p.position_id, p.position_title, s.skill_id, s.skill_name, ps.required_level
ORDER BY p.position_title, coverage_percent;
```

### 8. Interviewer Workload
```sql
-- Interviewer participation stats
SELECT
    CONCAT(e.first_name, ' ', e.last_name) as interviewer,
    d.department_name,
    e.position,
    COUNT(DISTINCT ip.interview_id) as interviews_assigned,
    COUNT(DISTINCT ie.evaluation_id) as evaluations_completed,
    ROUND(AVG(ie.overall_score), 2) as avg_score_given
FROM employees e
JOIN departments d ON e.department_id = d.department_id
LEFT JOIN interview_participants ip ON e.employee_id = ip.employee_id
LEFT JOIN interview_evaluations ie ON e.employee_id = ie.employee_id
WHERE e.status = 'active'
GROUP BY e.employee_id, e.first_name, e.last_name, d.department_name, e.position
ORDER BY interviews_assigned DESC;
```

### 9. Offer Status
```sql
-- All offers and their status
SELECT
    CONCAT(c.first_name, ' ', c.last_name) as candidate,
    p.position_title,
    o.offer_date,
    o.salary_offered,
    o.signing_bonus,
    o.start_date,
    o.status,
    DATEDIFF(o.expiry_date, CURDATE()) as days_until_expiry
FROM offers o
JOIN job_applications ja ON o.application_id = ja.application_id
JOIN candidates c ON ja.candidate_id = c.candidate_id
JOIN positions p ON ja.position_id = p.position_id
ORDER BY o.offer_date DESC;
```

### 10. Source of Hire Analysis
```sql
-- Recruitment channel effectiveness
SELECT
    source,
    COUNT(*) as total_candidates,
    SUM(CASE WHEN status = 'hired' THEN 1 ELSE 0 END) as hired,
    SUM(CASE WHEN status = 'offered' THEN 1 ELSE 0 END) as offered,
    SUM(CASE WHEN status = 'interviewing' THEN 1 ELSE 0 END) as interviewing,
    ROUND(SUM(CASE WHEN status = 'hired' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as hire_rate
FROM candidates
GROUP BY source
ORDER BY hired DESC;
```

---

## 🎯 Common Tasks

### Add New Candidate
```sql
INSERT INTO candidates (candidate_code, first_name, last_name, email, phone, years_experience, expected_salary_min, expected_salary_max, notice_period_days, source, status)
VALUES ('CAND016', 'Test', 'User', 'test.user@email.com', '+86-139-9999-9999', 5, 150000, 180000, 30, 'linkedin', 'applied');

-- Get the new candidate ID
SELECT LAST_INSERT_ID() as new_candidate_id;
```

### Schedule Interview
```sql
-- First, create a job application if needed
INSERT INTO job_applications (candidate_id, position_id, application_date, status)
VALUES (16, 1, CURDATE(), 'interviewing');

-- Get the application ID
SELECT LAST_INSERT_ID() as application_id;

-- Schedule interview
INSERT INTO interviews (application_id, stage_id, scheduled_date, duration_minutes, location, status)
VALUES (LAST_INSERT_ID(), 1, '2024-02-15 14:00:00', 30, NULL, 'scheduled');

-- Add interview participants
INSERT INTO interview_participants (interview_id, employee_id, role)
VALUES (LAST_INSERT_ID(), 1, 'lead_interviewer');
```

### Submit Evaluation
```sql
INSERT INTO interview_evaluations
(interview_id, employee_id, technical_score, communication_score,
 problem_solving_score, cultural_fit_score, overall_score, recommendation,
 strengths, weaknesses, additional_notes)
VALUES
(20, 1, 5, 4, 5, 4, 5, 'hire',
 'Excellent technical skills', 'None', 'Strong candidate');
```

### Update Candidate Status
```sql
UPDATE candidates SET status = 'hired' WHERE candidate_id = 12;
UPDATE job_applications SET status = 'hired' WHERE candidate_id = 12;
```

---

## 🔍 Search Queries

### Find Candidate by Email
```sql
SELECT * FROM v_candidate_summary WHERE email = 'search@email.com';
```

### Find Candidates by Skill
```sql
SELECT DISTINCT
    CONCAT(c.first_name, ' ', c.last_name) as candidate_name,
    c.email,
    c.years_experience,
    cs.proficiency_level
FROM candidates c
JOIN candidate_skills cs ON c.candidate_id = cs.candidate_id
JOIN skills s ON cs.skill_id = s.skill_id
WHERE s.skill_name = 'Python'
ORDER BY cs.proficiency_level, c.years_experience DESC;
```

### Find Interviews by Date Range
```sql
SELECT * FROM v_interview_details
WHERE DATE(scheduled_date) BETWEEN '2024-02-01' AND '2024-02-15'
ORDER BY scheduled_date;
```

---

## 📈 Reports

### Monthly Recruitment Report
```sql
SELECT
    MONTH(application_date) as month,
    COUNT(*) as applications,
    SUM(CASE WHEN status = 'hired' THEN 1 ELSE 0 END) as hired,
    SUM(CASE WHEN status = 'offered' THEN 1 ELSE 0 END) as offered,
    ROUND(SUM(CASE WHEN status = 'hired' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as hire_rate
FROM job_applications
WHERE application_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
GROUP BY MONTH(application_date)
ORDER BY month;
```

### Time to Hire Analysis
```sql
SELECT
    CONCAT(c.first_name, ' ', c.last_name) as candidate,
    p.position_title,
    ja.application_date,
    (SELECT MIN(scheduled_date) FROM interviews WHERE application_id = ja.application_id) as first_interview,
    o.offer_date,
    DATEDIFF(o.offer_date, ja.application_date) as days_to_offer
FROM job_applications ja
JOIN candidates c ON ja.candidate_id = c.candidate_id
JOIN positions p ON ja.position_id = p.position_id
LEFT JOIN offers o ON ja.application_id = o.application_id
WHERE ja.status IN ('hired', 'offered')
ORDER BY days_to_offer;
```

---

## 🛠️ Maintenance

### Clean Up Old Data
```sql
-- Archive withdrawn candidates
UPDATE candidates SET status = 'archived'
WHERE status = 'withdrawn'
  AND updated_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

### Update Statistics
```sql
ANALYZE TABLE candidates;
ANALYZE TABLE interviews;
ANALYZE TABLE interview_evaluations;
```

---

## 💡 Tips

1. **Use Views**: Use the provided views (`v_candidate_summary`, `v_interview_details`, etc.) for simpler queries
2. **Index Usage**: Queries on indexed fields (email, status, dates) are faster
3. **Date Formats**: Use `YYYY-MM-DD HH:MM:SS` for DATETIME fields
4. **Score Range**: All scores are 1-5, where 5 is best
5. **Recommendation Levels**: strong_hire > hire > neutral > no_hire > strong_no_hire

---

## 📞 Emergency Queries

### Cancel All Interviews for a Candidate
```sql
UPDATE interviews SET status = 'cancelled'
WHERE application_id IN (
    SELECT application_id FROM job_applications WHERE candidate_id = ?
);
```

### Withdraw Candidate
```sql
UPDATE candidates SET status = 'withdrawn' WHERE candidate_id = ?;
UPDATE job_applications SET status = 'withdrawn' WHERE candidate_id = ?;
UPDATE interviews SET status = 'cancelled'
WHERE application_id IN (SELECT application_id FROM job_applications WHERE candidate_id = ?);
```

---

**Last Updated**: 2024-02-06
**Database Version**: 1.0
