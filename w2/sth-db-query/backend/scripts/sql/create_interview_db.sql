-- ============================================================================
-- Interview Database Schema
-- 招聘面试管理系统数据库
-- ============================================================================

-- Drop database if exists and create new one
DROP DATABASE IF EXISTS interview_db;
CREATE DATABASE interview_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE interview_db;

-- ============================================================================
-- 1. Departments Table (部门表)
-- ============================================================================
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    manager_name VARCHAR(100),
    budget DECIMAL(15, 2),
    employee_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_department_code (department_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. Positions Table (职位表)
-- ============================================================================
CREATE TABLE positions (
    position_id INT AUTO_INCREMENT PRIMARY KEY,
    position_title VARCHAR(150) NOT NULL,
    position_code VARCHAR(30) NOT NULL UNIQUE,
    department_id INT NOT NULL,
    description TEXT,
    requirements TEXT,
    responsibilities TEXT,
    salary_min DECIMAL(12, 2),
    salary_max DECIMAL(12, 2),
    headcount INT DEFAULT 1,
    current_count INT DEFAULT 0,
    status ENUM('active', 'inactive', 'closed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT,
    INDEX idx_department (department_id),
    INDEX idx_status (status),
    INDEX idx_position_code (position_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. Employees Table (员工表 - 面试官)
-- ============================================================================
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department_id INT NOT NULL,
    position VARCHAR(100),
    hire_date DATE,
    status ENUM('active', 'inactive', 'on_leave') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT,
    INDEX idx_email (email),
    INDEX idx_department (department_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. Skills Table (技能表)
-- ============================================================================
CREATE TABLE skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category ENUM('technical', 'soft', 'language', 'tool') NOT NULL,
    description TEXT,
    proficiency_levels ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'intermediate',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_skill_name (skill_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. Position Skills Table (职位技能要求表)
-- ============================================================================
CREATE TABLE position_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position_id INT NOT NULL,
    skill_id INT NOT NULL,
    required_level ENUM('nice_to_have', 'required', 'must_have') DEFAULT 'required',
    years_experience INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions(position_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    UNIQUE KEY unique_position_skill (position_id, skill_id),
    INDEX idx_position (position_id),
    INDEX idx_skill (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 6. Interview Stages Table (面试阶段表)
-- ============================================================================
CREATE TABLE interview_stages (
    stage_id INT AUTO_INCREMENT PRIMARY KEY,
    stage_name VARCHAR(100) NOT NULL UNIQUE,
    stage_order INT NOT NULL UNIQUE,
    description TEXT,
    duration_minutes INT DEFAULT 60,
    is_group_interview BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stage_order (stage_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 7. Candidates Table (候选人表)
-- ============================================================================
CREATE TABLE candidates (
    candidate_id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    resume_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    years_experience INT DEFAULT 0,
    expected_salary_min DECIMAL(12, 2),
    expected_salary_max DECIMAL(12, 2),
    notice_period_days INT DEFAULT 30,
    source ENUM('linkedin', 'referral', 'indeed', 'career_site', 'recruiter', 'other') NOT NULL,
    status ENUM('applied', 'screening', 'interviewing', 'offered', 'hired', 'rejected', 'withdrawn') DEFAULT 'applied',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_source (source),
    INDEX idx_candidate_code (candidate_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 8. Candidate Skills Table (候选人技能表)
-- ============================================================================
CREATE TABLE candidate_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level ENUM('beginner', 'intermediate', 'advanced', 'expert') NOT NULL,
    years_experience INT DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    UNIQUE KEY unique_candidate_skill (candidate_id, skill_id),
    INDEX idx_candidate (candidate_id),
    INDEX idx_skill (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 9. Job Applications Table (职位申请表)
-- ============================================================================
CREATE TABLE job_applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    position_id INT NOT NULL,
    application_date DATE NOT NULL,
    status ENUM('applied', 'under_review', 'shortlisted', 'interviewing', 'offered', 'hired', 'rejected', 'withdrawn') DEFAULT 'applied',
    recruiter_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (position_id) REFERENCES positions(position_id) ON DELETE CASCADE,
    UNIQUE KEY unique_candidate_position (candidate_id, position_id),
    INDEX idx_candidate (candidate_id),
    INDEX idx_position (position_id),
    INDEX idx_status (status),
    INDEX idx_application_date (application_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 10. Interviews Table (面试安排表)
-- ============================================================================
CREATE TABLE interviews (
    interview_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    stage_id INT NOT NULL,
    scheduled_date DATETIME NOT NULL,
    duration_minutes INT DEFAULT 60,
    location VARCHAR(200),
    meeting_url VARCHAR(500),
    status ENUM('scheduled', 'completed', 'cancelled', 'no_show', 'rescheduled') DEFAULT 'scheduled',
    interviewer_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES job_applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (stage_id) REFERENCES interview_stages(stage_id) ON DELETE RESTRICT,
    INDEX idx_application (application_id),
    INDEX idx_stage (stage_id),
    INDEX idx_scheduled_date (scheduled_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 11. Interview Participants Table (面试参与者表)
-- ============================================================================
CREATE TABLE interview_participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    employee_id INT NOT NULL,
    role ENUM('lead_interviewer', 'interviewer', 'observer', 'panelist') DEFAULT 'interviewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(interview_id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    UNIQUE KEY unique_interview_employee (interview_id, employee_id),
    INDEX idx_interview (interview_id),
    INDEX idx_employee (employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 12. Interview Evaluations Table (面试评价表)
-- ============================================================================
CREATE TABLE interview_evaluations (
    evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    employee_id INT NOT NULL,
    technical_score INT CHECK (technical_score BETWEEN 1 AND 5),
    communication_score INT CHECK (communication_score BETWEEN 1 AND 5),
    problem_solving_score INT CHECK (problem_solving_score BETWEEN 1 AND 5),
    cultural_fit_score INT CHECK (cultural_fit_score BETWEEN 1 AND 5),
    overall_score INT CHECK (overall_score BETWEEN 1 AND 5),
    recommendation ENUM('strong_hire', 'hire', 'neutral', 'no_hire', 'strong_no_hire') NOT NULL,
    strengths TEXT,
    weaknesses TEXT,
    additional_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(interview_id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    UNIQUE KEY unique_interview_employee_eval (interview_id, employee_id),
    INDEX idx_interview (interview_id),
    INDEX idx_employee (employee_id),
    INDEX idx_recommendation (recommendation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 13. Offers Table (录用offer表)
-- ============================================================================
CREATE TABLE offers (
    offer_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    offer_date DATE NOT NULL,
    salary_offered DECIMAL(12, 2) NOT NULL,
    signing_bonus DECIMAL(12, 2),
    start_date DATE NOT NULL,
    status ENUM('pending', 'accepted', 'rejected', 'expired', 'withdrawn') DEFAULT 'pending',
    expiry_date DATE,
    terms TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES job_applications(application_id) ON DELETE CASCADE,
    INDEX idx_application (application_id),
    INDEX idx_status (status),
    INDEX idx_offer_date (offer_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Insert Seed Data
-- ============================================================================

-- 1. Departments
INSERT INTO departments (department_name, department_code, description, manager_name, budget, employee_count) VALUES
('Engineering', 'ENG', 'Software development and engineering', '张伟', 5000000.00, 45),
('Product Management', 'PM', 'Product strategy and management', '李娜', 1200000.00, 12),
('Design', 'DES', 'User experience and visual design', '王芳', 800000.00, 8),
('Marketing', 'MKT', 'Marketing and brand management', '刘强', 1500000.00, 15),
('Sales', 'SLS', 'Sales and business development', '陈杰', 2000000.00, 20),
('Human Resources', 'HR', 'Human resources and recruitment', '杨敏', 600000.00, 6),
('Finance', 'FIN', 'Finance and accounting', '赵丽', 900000.00, 8),
('Operations', 'OPS', 'Operations and logistics', '孙磊', 700000.00, 10);

-- 2. Interview Stages
INSERT INTO interview_stages (stage_name, stage_order, description, duration_minutes, is_group_interview) VALUES
('Phone Screen', 1, 'Initial phone screening with recruiter', 30, FALSE),
('Technical Assessment', 2, 'Online coding or technical test', 90, FALSE),
('Technical Interview', 3, 'Deep dive technical interview', 60, FALSE),
('System Design', 4, 'System design interview for senior roles', 60, FALSE),
('Behavioral Interview', 5, 'Behavioral and cultural fit interview', 45, FALSE),
('Panel Interview', 6, 'Panel interview with multiple interviewers', 90, TRUE),
('Manager Interview', 7, 'Interview with hiring manager', 45, FALSE),
('Executive Interview', 8, 'Final interview with executive', 30, FALSE);

-- 3. Skills
INSERT INTO skills (skill_name, category, description, proficiency_levels) VALUES
-- Technical Skills
('Python', 'technical', 'Python programming language', 'intermediate'),
('Java', 'technical', 'Java programming language', 'intermediate'),
('JavaScript', 'technical', 'JavaScript programming language', 'intermediate'),
('TypeScript', 'technical', 'TypeScript programming language', 'intermediate'),
('React', 'technical', 'React.js framework', 'intermediate'),
('Vue.js', 'technical', 'Vue.js framework', 'intermediate'),
('Node.js', 'technical', 'Node.js runtime', 'intermediate'),
('SQL', 'technical', 'Structured Query Language', 'intermediate'),
('NoSQL', 'technical', 'NoSQL databases (MongoDB, Redis)', 'intermediate'),
('AWS', 'technical', 'Amazon Web Services', 'intermediate'),
('Docker', 'technical', 'Docker containerization', 'intermediate'),
('Kubernetes', 'technical', 'Kubernetes orchestration', 'intermediate'),
('Git', 'technical', 'Version control with Git', 'intermediate'),
('RESTful APIs', 'technical', 'RESTful API design', 'intermediate'),
('GraphQL', 'technical', 'GraphQL query language', 'intermediate'),
('Microservices', 'technical', 'Microservices architecture', 'advanced'),
('Machine Learning', 'technical', 'ML algorithms and frameworks', 'advanced'),
('Data Structures', 'technical', 'Data structures and algorithms', 'intermediate'),
('System Design', 'technical', 'Large-scale system design', 'advanced'),
('CI/CD', 'technical', 'Continuous Integration/Deployment', 'intermediate'),
('Testing', 'technical', 'Unit and integration testing', 'intermediate'),

-- Soft Skills
('Communication', 'soft', 'Verbal and written communication', 'intermediate'),
('Leadership', 'soft', 'Leadership and people management', 'intermediate'),
('Teamwork', 'soft', 'Collaboration and teamwork', 'intermediate'),
('Problem Solving', 'soft', 'Analytical problem solving', 'intermediate'),
('Time Management', 'soft', 'Time management and prioritization', 'intermediate'),
('Adaptability', 'soft', 'Adaptability and learning agility', 'intermediate'),
('Creativity', 'soft', 'Creative thinking and innovation', 'intermediate'),
('Critical Thinking', 'soft', 'Critical thinking and analysis', 'intermediate'),

-- Language Skills
('English', 'language', 'English language proficiency', 'intermediate'),
('Mandarin Chinese', 'language', 'Mandarin Chinese proficiency', 'intermediate'),
('Spanish', 'language', 'Spanish language proficiency', 'beginner'),
('French', 'language', 'French language proficiency', 'beginner'),

-- Tools
('Jira', 'tool', 'Jira project management', 'intermediate'),
('Confluence', 'tool', 'Confluence documentation', 'beginner'),
('Slack', 'tool', 'Slack communication', 'beginner'),
('Figma', 'tool', 'Figma design tool', 'intermediate'),
('Excel', 'tool', 'Microsoft Excel', 'intermediate'),
('PowerPoint', 'tool', 'Microsoft PowerPoint', 'beginner');

-- 4. Positions
INSERT INTO positions (position_title, position_code, department_id, description, requirements, responsibilities, salary_min, salary_max, headcount, current_count, status) VALUES
('Senior Software Engineer', 'SSE-001', 1, 'Senior software engineer position for backend development', '5+ years of experience in Python/Java, strong knowledge of databases and cloud services', 'Design and implement scalable backend services, mentor junior engineers', 150000.00, 200000.00, 3, 2, 'active'),
('Full Stack Developer', 'FSD-002', 1, 'Full stack developer for web applications', '3+ years of experience with React and Node.js', 'Develop and maintain web applications', 120000.00, 160000.00, 2, 1, 'active'),
('DevOps Engineer', 'DOE-003', 1, 'DevOps engineer for infrastructure and CI/CD', '3+ years of experience with AWS, Docker, Kubernetes', 'Build and maintain CI/CD pipelines, manage cloud infrastructure', 140000.00, 180000.00, 2, 1, 'active'),
('Data Engineer', 'DE-004', 1, 'Data engineer for data pipeline and analytics', '4+ years of experience with ETL, SQL, and big data technologies', 'Design and build data pipelines', 130000.00, 170000.00, 1, 0, 'active'),
('ML Engineer', 'MLE-005', 1, 'Machine learning engineer for AI/ML projects', '3+ years of experience with ML frameworks and Python', 'Develop and deploy ML models', 150000.00, 210000.00, 1, 0, 'active'),
('Product Manager', 'PM-101', 2, 'Product manager for web products', '4+ years of product management experience', 'Define product roadmap and work with engineering', 140000.00, 180000.00, 1, 0, 'active'),
('UI/UX Designer', 'UID-201', 3, 'UI/UX designer for user experience design', '3+ years of experience with Figma and design systems', 'Create user-centered designs', 110000.00, 150000.00, 2, 1, 'active'),
('Marketing Manager', 'MMK-301', 4, 'Marketing manager for digital marketing', '5+ years of digital marketing experience', 'Lead marketing campaigns and strategies', 120000.00, 160000.00, 1, 1, 'active'),
('Sales Representative', 'SLS-401', 5, 'Sales representative for enterprise sales', '2+ years of B2B sales experience', 'Generate leads and close deals', 80000.00, 120000.00, 3, 2, 'active'),
('HR Coordinator', 'HRC-501', 6, 'HR coordinator for recruitment', '2+ years of HR experience', 'Coordinate recruitment and onboarding', 60000.00, 80000.00, 1, 1, 'active');

-- 5. Position Skills (Senior Software Engineer)
INSERT INTO position_skills (position_id, skill_id, required_level, years_experience) SELECT 1, skill_id, 'must_have', 3 FROM skills WHERE skill_name IN ('Python', 'SQL', 'RESTful APIs', 'Git', 'System Design');
INSERT INTO position_skills (position_id, skill_id, required_level, years_experience) SELECT 1, skill_id, 'required', 2 FROM skills WHERE skill_name IN ('Docker', 'AWS', 'Testing', 'Microservices');

-- 6. Position Skills (Full Stack Developer)
INSERT INTO position_skills (position_id, skill_id, required_level, years_experience) SELECT 2, skill_id, 'must_have', 3 FROM skills WHERE skill_name IN ('JavaScript', 'React', 'Node.js', 'SQL');
INSERT INTO position_skills (position_id, skill_id, required_level, years_experience) SELECT 2, skill_id, 'required', 2 FROM skills WHERE skill_name IN ('TypeScript', 'Git', 'RESTful APIs');

-- 7. Position Skills (DevOps Engineer)
INSERT INTO position_skills (position_id, skill_id, required_level, years_experience) SELECT 3, skill_id, 'must_have', 3 FROM skills WHERE skill_name IN ('AWS', 'Docker', 'Kubernetes', 'CI/CD');
INSERT INTO position_skills (position_id, skill_id, required_level, years_experience) SELECT 3, skill_id, 'required', 2 FROM skills WHERE skill_name IN ('Git', 'Python', 'System Design');

-- 8. Position Skills (Product Manager)
INSERT INTO position_skills (position_id, skill_id, required_level, years_experience) SELECT 6, skill_id, 'must_have', 4 FROM skills WHERE skill_name IN ('Communication', 'Leadership', 'Problem Solving');
INSERT INTO position_skills (position_id, skill_id, required_level) SELECT 6, skill_id, 'required' FROM skills WHERE skill_name IN ('Agile', 'Jira', 'English');

-- 9. Employees (Interviewers)
INSERT INTO employees (employee_code, first_name, last_name, email, phone, department_id, position, hire_date, status) VALUES
('EMP001', '建国', '李', 'jianguo.li@company.com', '+86-138-0000-0001', 1, 'Tech Lead', '2020-03-15', 'active'),
('EMP002', '淑华', '王', 'shuhua.wang@company.com', '+86-138-0000-0002', 1, 'Senior Developer', '2019-07-20', 'active'),
('EMP003', '明', '张', 'ming.zhang@company.com', '+86-138-0000-0003', 1, 'Backend Developer', '2021-01-10', 'active'),
('EMP004', '丽', '陈', 'li.chen@company.com', '+86-138-0000-0004', 1, 'Full Stack Developer', '2021-06-01', 'active'),
('EMP005', '强', '刘', 'qiang.liu@company.com', '+86-138-0000-0005', 1, 'DevOps Engineer', '2020-09-15', 'active'),
('EMP006', '伟', '杨', 'wei.yang@company.com', '+86-138-0000-0006', 2, 'Senior Product Manager', '2018-04-01', 'active'),
('EMP007', '娜', '赵', 'na.zhao@company.com', '+86-138-0000-0007', 2, 'Product Manager', '2021-03-20', 'active'),
('EMP008', '敏', '孙', 'min.sun@company.com', '+86-138-0000-0008', 3, 'Lead Designer', '2019-11-10', 'active'),
('EMP009', '杰', '周', 'jie.zhou@company.com', '+86-138-0000-0009', 3, 'UI Designer', '2022-01-05', 'active'),
('EMP010', '磊', '吴', 'lei.wu@company.com', '+86-138-0000-0010', 4, 'Marketing Manager', '2020-05-15', 'active'),
('EMP011', '芳', '郑', 'fang.zheng@company.com', '+86-138-0000-0011', 5, 'Sales Manager', '2019-08-20', 'active'),
('EMP012', '秀英', '黄', 'xiuying.huang@company.com', '+86-138-0000-0012', 6, 'HR Manager', '2018-02-01', 'active'),
('EMP013', '勇', '徐', 'yong.xu@company.com', '+86-138-0000-0013', 1, 'Principal Engineer', '2017-06-15', 'active'),
('EMP014', '军', '朱', 'jun.zhu@company.com', '+86-138-0000-0014', 1, 'Data Engineer', '2021-09-01', 'active'),
('EMP015', '静', '高', 'jing.gao@company.com', '+86-138-0000-0015', 2, 'Senior PM', '2019-12-10', 'active');

-- 10. Candidates
INSERT INTO candidates (candidate_code, first_name, last_name, email, phone, years_experience, expected_salary_min, expected_salary_max, notice_period_days, source, status) VALUES
('CAND001', '子轩', '林', 'zixuan.lin@email.com', '+86-139-0001-0001', 6, 160000, 200000, 45, 'linkedin', 'interviewing'),
('CAND002', '欣怡', '黄', 'xinyi.huang@email.com', '+86-139-0001-0002', 4, 130000, 160000, 30, 'referral', 'interviewing'),
('CAND003', '浩宇', '王', 'haoyu.wang@email.com', '+86-139-0001-0003', 5, 150000, 180000, 60, 'indeed', 'interviewing'),
('CAND004', '梓涵', '李', 'zihan.li@email.com', '+86-139-0001-0004', 3, 120000, 150000, 15, 'linkedin', 'interviewing'),
('CAND005', '一诺', '张', 'yinuo.zhang@email.com', '+86-139-0001-0005', 7, 180000, 220000, 90, 'referral', 'interviewing'),
('CAND006', '思睿', '刘', 'sirui.liu@email.com', '+86-139-0001-0006', 4, 140000, 170000, 30, 'career_site', 'screening'),
('CAND007', '雨桐', '陈', 'yutong.chen@email.com', '+86-139-0001-0007', 2, 100000, 130000, 14, 'linkedin', 'interviewing'),
('CAND008', '博文', '杨', 'bowen.yang@email.com', '+86-139-0001-0008', 5, 155000, 185000, 30, 'recruiter', 'interviewing'),
('CAND009', '梦琪', '赵', 'mengqi.zhao@email.com', '+86-139-0001-0009', 3, 115000, 145000, 20, 'indeed', 'applied'),
('CAND010', '宇航', '周', 'yuhang.zhou@email.com', '+86-139-0001-0010', 6, 165000, 195000, 45, 'linkedin', 'interviewing'),
('CAND011', '子萱', '吴', 'zixuan.wu@email.com', '+86-139-0001-0011', 4, 125000, 155000, 30, 'referral', 'interviewing'),
('CAND012', '天宇', '徐', 'tianyu.xu@email.com', '+86-139-0001-0012', 8, 200000, 250000, 60, 'linkedin', 'offered'),
('CAND013', '欣妍', '孙', 'xinyan.sun@email.com', '+86-139-0001-0013', 3, 110000, 140000, 21, 'career_site', 'interviewing'),
('CAND014', '俊杰', '马', 'junjie.ma@email.com', '+86-139-0001-0014', 5, 145000, 175000, 30, 'recruiter', 'interviewing'),
('CAND015', '雅琳', '朱', 'yalin.zhu@email.com', '+86-139-0001-0015', 2, 95000, 125000, 15, 'indeed', 'applied');

-- 11. Candidate Skills
INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 1, skill_id, 'expert', 6, TRUE FROM skills WHERE skill_name IN ('Python', 'SQL', 'System Design', 'Microservices');
INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 1, skill_id, 'advanced', 4, TRUE FROM skills WHERE skill_name IN ('AWS', 'Docker', 'Kubernetes');

INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 2, skill_id, 'advanced', 4, TRUE FROM skills WHERE skill_name IN ('JavaScript', 'React', 'Node.js', 'TypeScript');
INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 2, skill_id, 'intermediate', 2, FALSE FROM skills WHERE skill_name IN ('GraphQL', 'Docker');

INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 3, skill_id, 'expert', 5, TRUE FROM skills WHERE skill_name IN ('Java', 'Spring', 'SQL', 'System Design');
INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 3, skill_id, 'advanced', 3, TRUE FROM skills WHERE skill_name IN ('AWS', 'Microservices');

INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 4, skill_id, 'advanced', 3, TRUE FROM skills WHERE skill_name IN ('Python', 'Django', 'JavaScript', 'React');
INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 4, skill_id, 'intermediate', 2, FALSE FROM skills WHERE skill_name IN ('SQL', 'Git', 'Testing');

INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 5, skill_id, 'expert', 7, TRUE FROM skills WHERE skill_name IN ('Python', 'Machine Learning', 'SQL', 'System Design');
INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 5, skill_id, 'advanced', 5, TRUE FROM skills WHERE skill_name IN ('AWS', 'Kubernetes', 'Data Structures');

INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 6, skill_id, 'advanced', 4, TRUE FROM skills WHERE skill_name IN ('Docker', 'Kubernetes', 'CI/CD', 'AWS');
INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 6, skill_id, 'intermediate', 3, TRUE FROM skills WHERE skill_name IN ('Git', 'Python', 'System Design');

INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 7, skill_id, 'intermediate', 2, FALSE FROM skills WHERE skill_name IN ('Figma', 'UI Design');
INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 7, skill_id, 'advanced', 3, TRUE FROM skills WHERE skill_name IN ('Communication', 'Teamwork');

INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 8, skill_id, 'advanced', 5, TRUE FROM skills WHERE skill_name IN ('SQL', 'NoSQL', 'Python', 'Data Engineering');
INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level, years_experience, verified)
SELECT 8, skill_id, 'intermediate', 3, TRUE FROM skills WHERE skill_name IN ('AWS', 'Docker', 'ETL');

-- 12. Job Applications
INSERT INTO job_applications (candidate_id, position_id, application_date, status, recruiter_notes) VALUES
(1, 1, '2024-01-15', 'interviewing', 'Strong technical background, good fit for SSE role'),
(2, 2, '2024-01-18', 'interviewing', 'Excellent full stack skills'),
(3, 1, '2024-01-20', 'interviewing', 'Senior Java developer, good system design knowledge'),
(4, 2, '2024-01-22', 'interviewing', 'Solid full stack experience'),
(5, 5, '2024-01-10', 'interviewing', 'Exceptional ML background, PhD in CS'),
(6, 3, '2024-01-25', 'screening', 'DevOps experience, pending review'),
(7, 7, '2024-01-28', 'interviewing', 'Good portfolio, strong UI skills'),
(8, 4, '2024-01-12', 'interviewing', 'Strong data engineering background'),
(9, 2, '2024-01-30', 'applied', 'Recent application, under review'),
(10, 1, '2024-01-08', 'interviewing', 'Very experienced, former tech lead'),
(11, 2, '2024-02-01', 'interviewing', 'Referred by EMP002, strong React skills'),
(12, 1, '2024-01-05', 'offered', 'Outstanding candidate, extended offer'),
(13, 7, '2024-02-03', 'interviewing', 'Creative designer with good UX sense'),
(14, 3, '2024-02-05', 'interviewing', 'Solid DevOps skills, AWS certified'),
(15, 7, '2024-02-06', 'applied', 'Recent application from career site');

-- 13. Interviews (scheduled interviews)
INSERT INTO interviews (application_id, stage_id, scheduled_date, duration_minutes, location, meeting_url, status) VALUES
-- Candidate 1 - Senior Software Engineer
(1, 1, '2024-02-01 10:00:00', 30, NULL, 'https://zoom.us/j/123456789', 'completed'),
(1, 2, '2024-02-03 14:00:00', 90, NULL, 'https://hackerrank.com/test/interview1', 'completed'),
(1, 3, '2024-02-05 15:00:00', 60, 'Meeting Room A', NULL, 'completed'),
(1, 4, '2024-02-07 14:00:00', 60, 'Meeting Room B', NULL, 'scheduled'),

-- Candidate 2 - Full Stack Developer
(2, 1, '2024-02-05 11:00:00', 30, NULL, 'https://zoom.us/j/234567890', 'completed'),
(2, 3, '2024-02-07 15:30:00', 60, 'Meeting Room C', NULL, 'completed'),
(2, 5, '2024-02-09 11:00:00', 45, 'Meeting Room A', NULL, 'scheduled'),

-- Candidate 3 - Senior Software Engineer
(3, 1, '2024-02-06 10:30:00', 30, NULL, 'https://zoom.us/j/345678901', 'completed'),
(3, 2, '2024-02-08 13:00:00', 90, NULL, 'https://hackerrank.com/test/interview3', 'completed'),
(3, 3, '2024-02-10 14:00:00', 60, 'Meeting Room D', NULL, 'scheduled'),

-- Candidate 5 - ML Engineer
(5, 1, '2024-01-25 09:00:00', 30, NULL, 'https://zoom.us/j/456789012', 'completed'),
(5, 2, '2024-01-27 14:00:00', 90, NULL, 'https://hackerrank.com/test/interview5', 'completed'),
(5, 3, '2024-01-29 15:00:00', 60, 'Meeting Room E', NULL, 'completed'),
(5, 4, '2024-01-31 14:00:00', 60, 'Meeting Room A', NULL, 'completed'),
(5, 7, '2024-02-02 10:00:00', 45, 'Executive Office', NULL, 'completed'),

-- Candidate 12 - Offered
(12, 1, '2024-01-08 11:00:00', 30, NULL, 'https://zoom.us/j/567890123', 'completed'),
(12, 2, '2024-01-10 14:00:00', 90, NULL, 'https://hackerrank.com/test/interview12', 'completed'),
(12, 3, '2024-01-12 15:00:00', 60, 'Meeting Room A', NULL, 'completed'),
(12, 4, '2024-01-15 14:00:00', 60, 'Meeting Room B', NULL, 'completed'),
(12, 5, '2024-01-17 11:00:00', 45, 'Meeting Room C', NULL, 'completed'),
(12, 6, '2024-01-19 14:00:00', 90, 'Conference Room', NULL, 'completed'),
(12, 7, '2024-01-22 10:00:00', 30, 'Executive Office', NULL, 'completed');

-- 14. Interview Participants
INSERT INTO interview_participants (interview_id, employee_id, role) VALUES
-- Interview 1 - Phone Screen
(1, 12, 'lead_interviewer'),

-- Interview 2 - Technical Assessment
(2, 2, 'observer'),

-- Interview 3 - Technical Interview
(3, 1, 'lead_interviewer'),
(3, 2, 'interviewer'),
(3, 13, 'observer'),

-- Interview 4 - System Design
(4, 1, 'lead_interviewer'),
(4, 13, 'interviewer'),

-- Interview 5 - Phone Screen
(5, 12, 'lead_interviewer'),

-- Interview 6 - Technical Interview
(6, 2, 'lead_interviewer'),
(6, 4, 'interviewer'),

-- Interview 7 - Behavioral Interview
(7, 12, 'lead_interviewer'),

-- Interview 8-12 - Candidate 5 (ML Engineer)
(8, 12, 'lead_interviewer'),
(9, 2, 'observer'),
(10, 1, 'lead_interviewer'),
(10, 14, 'interviewer'),
(11, 13, 'lead_interviewer'),
(11, 5, 'interviewer'),
(12, 15, 'lead_interviewer'),

-- Interview 13-19 - Candidate 12 (Offered)
(13, 12, 'lead_interviewer'),
(14, 2, 'observer'),
(15, 1, 'lead_interviewer'),
(15, 2, 'interviewer'),
(15, 13, 'observer'),
(16, 13, 'lead_interviewer'),
(16, 5, 'interviewer'),
(17, 6, 'lead_interviewer'),
(17, 15, 'interviewer'),
(18, 1, 'lead_interviewer'),
(18, 6, 'panelist'),
(18, 15, 'panelist'),
(18, 13, 'panelist'),
(19, 6, 'lead_interviewer');

-- 15. Interview Evaluations
INSERT INTO interview_evaluations (interview_id, employee_id, technical_score, communication_score, problem_solving_score, cultural_fit_score, overall_score, recommendation, strengths, weaknesses, additional_notes) VALUES
-- Candidate 1 evaluations
(3, 1, 5, 4, 5, 4, 5, 'strong_hire', 'Excellent Python skills, strong system design knowledge', 'Could improve on documentation', 'Very strong technical candidate'),
(3, 2, 4, 4, 4, 5, 4, 'hire', 'Good technical skills, great team player', 'None observed', 'Would be a great addition to the team'),
(3, 13, 5, 5, 5, 4, 5, 'strong_hire', 'Exceptional problem solving, deep technical expertise', 'Sometimes too detail-oriented', 'Principal level engineer'),

-- Candidate 2 evaluations
(6, 2, 4, 5, 4, 5, 4, 'hire', 'Strong React and Node.js skills, excellent communication', 'Limited backend experience', 'Great full stack developer'),
(6, 4, 4, 4, 4, 4, 4, 'hire', 'Solid technical skills, good front-end expertise', 'Could learn more about state management', 'Good cultural fit'),

-- Candidate 3 evaluations
(10, 1, 5, 4, 5, 4, 5, 'hire', 'Strong Java background, good system design', 'A bit quiet during interview', 'Technical skills are excellent'),
(10, 13, 4, 4, 4, 4, 4, 'hire', 'Good architectural knowledge', 'Could improve on explaining trade-offs', 'Solid senior engineer'),

-- Candidate 5 evaluations (ML Engineer)
(10, 1, 5, 5, 5, 5, 5, 'strong_hire', 'Outstanding ML knowledge, exceptional problem solving', 'None significant', 'One of the best candidates I have interviewed'),
(10, 14, 5, 4, 5, 5, 5, 'strong_hire', 'Deep understanding of ML algorithms and frameworks', 'Could improve on explaining complex concepts', 'Expert level data engineer'),
(11, 13, 5, 5, 5, 5, 5, 'strong_hire', 'Brilliant system design for ML pipeline', 'None', 'Principal level candidate'),
(11, 5, 4, 4, 5, 5, 4, 'hire', 'Good understanding of infrastructure needs', 'Limited DevOps experience', 'Strong ML engineering background'),
(12, 15, 5, 5, 5, 5, 5, 'strong_hire', 'Excellent product thinking, great communication', 'None', 'Would be great for the ML team'),

-- Candidate 12 evaluations (Offered)
(15, 1, 5, 5, 5, 5, 5, 'strong_hire', 'Perfect technical fit, exceptional skills', 'None', 'Ideal candidate for SSE role'),
(15, 2, 5, 5, 5, 5, 5, 'strong_hire', 'Outstanding coding abilities, great problem solver', 'None', 'Top 1% of candidates'),
(15, 13, 5, 5, 5, 5, 5, 'strong_hire', 'Principal level engineering skills', 'None', 'Should consider for tech lead role'),
(16, 13, 5, 5, 5, 5, 5, 'strong_hire', 'Brilliant system design, scalability expert', 'None', 'Can architect large-scale systems'),
(16, 5, 4, 5, 5, 5, 4, 'hire', 'Good understanding of infrastructure', 'Could learn more about Kubernetes', 'Strong overall'),
(17, 6, 5, 5, 5, 5, 5, 'strong_hire', 'Excellent product sense, great leadership', 'None', 'Strong PM skills'),
(17, 15, 5, 5, 5, 5, 5, 'strong_hire', 'Strategic thinker, great communicator', 'None', 'Executive material'),
(18, 1, 5, 5, 5, 5, 5, 'strong_hire', 'Technical excellence, great culture fit', 'None', 'Unanimous hire decision'),
(18, 6, 5, 5, 5, 5, 5, 'strong_hire', 'Strong leadership potential', 'None', 'Future leader'),
(18, 15, 5, 5, 5, 5, 5, 'strong_hire', 'Exceptional all-around candidate', 'None', 'Must hire'),
(18, 13, 5, 5, 5, 5, 5, 'strong_hire', 'Principal level technical skills', 'None', 'Top tier candidate'),
(19, 6, 5, 5, 5, 5, 5, 'strong_hire', 'Ready for leadership role', 'None', 'Immediate hire');

-- 16. Offers
INSERT INTO offers (application_id, offer_date, salary_offered, signing_bonus, start_date, status, expiry_date, terms) VALUES
(12, '2024-01-25', 210000.00, 20000.00, '2024-03-01', 'pending', '2024-02-15', 'Standard benefits package, stock options, flexible work hours');

-- ============================================================================
-- Useful Views for Reporting
-- ============================================================================

CREATE VIEW v_candidate_summary AS
SELECT
    c.candidate_id,
    c.candidate_code,
    c.first_name,
    c.last_name,
    c.email,
    c.phone,
    c.years_experience,
    c.source,
    c.status as candidate_status,
    p.position_title,
    d.department_name,
    ja.application_date,
    ja.status as application_status
FROM candidates c
JOIN job_applications ja ON c.candidate_id = ja.candidate_id
JOIN positions p ON ja.position_id = p.position_id
JOIN departments d ON p.department_id = d.department_id;

CREATE VIEW v_interview_details AS
SELECT
    i.interview_id,
    c.candidate_code,
    CONCAT(c.first_name, ' ', c.last_name) as candidate_name,
    p.position_title,
    s.stage_name,
    i.scheduled_date,
    i.duration_minutes,
    i.location,
    i.meeting_url,
    i.status as interview_status,
    COUNT(DISTINCT ip.employee_id) as interviewer_count
FROM interviews i
JOIN job_applications ja ON i.application_id = ja.application_id
JOIN candidates c ON ja.candidate_id = c.candidate_id
JOIN positions p ON ja.position_id = p.position_id
JOIN interview_stages s ON i.stage_id = s.stage_id
LEFT JOIN interview_participants ip ON i.interview_id = ip.interview_id
GROUP BY i.interview_id, c.candidate_code, c.first_name, c.last_name, p.position_title, s.stage_name, i.scheduled_date, i.duration_minutes, i.location, i.meeting_url, i.status;

CREATE VIEW v_evaluation_summary AS
SELECT
    ie.evaluation_id,
    c.candidate_code,
    CONCAT(c.first_name, ' ', c.last_name) as candidate_name,
    p.position_title,
    s.stage_name,
    CONCAT(e.first_name, ' ', e.last_name) as interviewer_name,
    ie.technical_score,
    ie.communication_score,
    ie.problem_solving_score,
    ie.cultural_fit_score,
    ie.overall_score,
    ie.recommendation
FROM interview_evaluations ie
JOIN interviews i ON ie.interview_id = i.interview_id
JOIN job_applications ja ON i.application_id = ja.application_id
JOIN candidates c ON ja.candidate_id = c.candidate_id
JOIN positions p ON ja.position_id = p.position_id
JOIN interview_stages s ON i.stage_id = s.stage_id
JOIN employees e ON ie.employee_id = e.employee_id;

CREATE VIEW v_open_positions_summary AS
SELECT
    p.position_id,
    p.position_title,
    p.position_code,
    d.department_name,
    p.description,
    p.salary_min,
    p.salary_max,
    p.headcount,
    p.current_count,
    (p.headcount - p.current_count) as openings,
    p.status,
    COUNT(DISTINCT ja.candidate_id) as total_applicants,
    SUM(CASE WHEN ja.status = 'interviewing' THEN 1 ELSE 0 END) as interviewing,
    SUM(CASE WHEN ja.status = 'offered' THEN 1 ELSE 0 END) as offered,
    SUM(CASE WHEN ja.status = 'hired' THEN 1 ELSE 0 END) as hired
FROM positions p
JOIN departments d ON p.department_id = d.department_id
LEFT JOIN job_applications ja ON p.position_id = ja.position_id
WHERE p.status = 'active'
GROUP BY p.position_id, p.position_title, p.position_code, d.department_name, p.description, p.salary_min, p.salary_max, p.headcount, p.current_count, p.status;

-- ============================================================================
-- Display Summary Statistics
-- ============================================================================

SELECT 'Database Setup Complete!' as status;
SELECT COUNT(*) as total_departments FROM departments;
SELECT COUNT(*) as total_positions FROM positions;
SELECT COUNT(*) as total_employees FROM employees;
SELECT COUNT(*) as total_candidates FROM candidates;
SELECT COUNT(*) as total_interviews FROM interviews;
SELECT COUNT(*) as total_evaluations FROM interview_evaluations;
