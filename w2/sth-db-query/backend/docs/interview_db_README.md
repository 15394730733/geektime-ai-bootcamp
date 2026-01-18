# Interview Database (interview_db)

一个完整的招聘面试管理系统数据库，用于记录公司招聘流程中的候选人信息、面试安排、评价结果等。

## 📊 数据库概述

### 核心功能
- 候选人信息管理
- 职位申请跟踪
- 面试安排与协调
- 面试评价与反馈
- Offer 管理
- 技能匹配分析
- 招聘数据报表

### 数据库规模
- **13 个核心表**
- **4 个实用视图**
- **15 名候选人**
- **10 个职位**
- **8 个部门**
- **15 名员工（面试官）**
- **30+ 种技能**
- **19 场面试**
- **13 条评价记录**

## 🗂️ 数据库表结构

### 1. **departments** (部门表)
公司的组织结构部门信息。

**关键字段**:
- department_id (主键)
- department_name, department_code
- manager_name, budget, employee_count

### 2. **positions** (职位表)
招聘的职位信息。

**关键字段**:
- position_id (主键)
- position_title, position_code
- department_id (外键)
- salary_min, salary_max, headcount
- status (active/inactive/closed)

### 3. **employees** (员工表)
公司员工信息，主要用于面试官。

**关键字段**:
- employee_id (主键)
- employee_code, first_name, last_name
- email, phone
- department_id (外键)
- position, hire_date, status

### 4. **skills** (技能表)
技能分类管理。

**关键字段**:
- skill_id (主键)
- skill_name, category (technical/soft/language/tool)
- description, proficiency_levels

**技能类别**:
- Technical: Python, Java, JavaScript, React, AWS, Docker, Kubernetes 等
- Soft Skills: Communication, Leadership, Teamwork 等
- Languages: English, Mandarin, Spanish, French
- Tools: Jira, Confluence, Slack, Figma 等

### 5. **position_skills** (职位技能要求表)
职位与技能的关联关系，定义职位需要的技能及熟练度要求。

**关键字段**:
- position_id (外键)
- skill_id (外键)
- required_level (nice_to_have/required/must_have)
- years_experience

### 6. **interview_stages** (面试阶段表)
定义面试流程的各个阶段。

**面试阶段**:
1. Phone Screen (电话筛选)
2. Technical Assessment (技术评估)
3. Technical Interview (技术面试)
4. System Design (系统设计)
5. Behavioral Interview (行为面试)
6. Panel Interview (小组面试)
7. Manager Interview (经理面试)
8. Executive Interview (高管面试)

### 7. **candidates** (候选人表)
求职者的基本信息。

**关键字段**:
- candidate_id (主键)
- candidate_code, first_name, last_name
- email, phone
- years_experience
- expected_salary_min, expected_salary_max
- source (linkedin/referral/indeed/career_site/recruiter/other)
- status (applied/screening/interviewing/offered/hired/rejected/withdrawn)

### 8. **candidate_skills** (候选人技能表)
候选人掌握的技能及熟练程度。

**关键字段**:
- candidate_id (外键)
- skill_id (外键)
- proficiency_level (beginner/intermediate/advanced/expert)
- years_experience, verified

### 9. **job_applications** (职位申请表)
候选人对特定职位的申请记录。

**关键字段**:
- application_id (主键)
- candidate_id (外键)
- position_id (外键)
- application_date
- status, recruiter_notes

### 10. **interviews** (面试安排表)
面试的具体安排信息。

**关键字段**:
- interview_id (主键)
- application_id (外键)
- stage_id (外键)
- scheduled_date, duration_minutes
- location, meeting_url
- status (scheduled/completed/cancelled/no_show/rescheduled)

### 11. **interview_participants** (面试参与者表)
面试参与的面试官信息。

**关键字段**:
- interview_id (外键)
- employee_id (外键)
- role (lead_interviewer/interviewer/observer/panelist)

### 12. **interview_evaluations** (面试评价表)
面试官对候选人的评价。

**关键字段**:
- evaluation_id (主键)
- interview_id (外键)
- employee_id (外键)
- technical_score, communication_score
- problem_solving_score, cultural_fit_score, overall_score (1-5分)
- recommendation (strong_hire/hire/neutral/no_hire/strong_no_hire)
- strengths, weaknesses, additional_notes

### 13. **offers** (录用offer表)
向候选人发出的录用通知。

**关键字段**:
- offer_id (主键)
- application_id (外键)
- offer_date, salary_offered, signing_bonus
- start_date, status, expiry_date
- terms

## 📈 数据库视图

### 1. **v_candidate_summary**
候选人概览视图，包含候选人、职位、部门等综合信息。

**示例查询**:
```sql
SELECT * FROM v_candidate_summary WHERE candidate_status = 'interviewing';
```

### 2. **v_interview_details**
面试详情视图，包含面试安排、候选人、面试官等信息。

**示例查询**:
```sql
SELECT * FROM v_interview_details WHERE scheduled_date > NOW();
```

### 3. **v_evaluation_summary**
评价汇总视图，包含所有面试评价的详细信息。

**示例查询**:
```sql
SELECT
    candidate_name,
    interviewer_name,
    stage_name,
    overall_score,
    recommendation
FROM v_evaluation_summary
ORDER BY overall_score DESC;
```

### 4. **v_open_positions_summary**
空缺职位汇总视图，包含职位申请统计信息。

**示例查询**:
```sql
SELECT * FROM v_open_positions_summary WHERE openings > 0;
```

## 🔧 安装和使用

### 安装数据库

```bash
# 使用 MySQL 命令行
mysql -u root -p < create_interview_db.sql

# 或在 MySQL 客户器中
source /path/to/create_interview_db.sql;
```

### 连接数据库

```bash
mysql -u root -p
USE interview_db;
```

## 📝 示例查询

### 1. 查看所有部门
```sql
SELECT department_name, manager_name, employee_count, budget
FROM departments
ORDER BY employee_count DESC;
```

### 2. 查看当前空缺职位
```sql
SELECT
    position_title,
    department_name,
    salary_min,
    salary_max,
    (headcount - current_count) as openings
FROM v_open_positions_summary
WHERE openings > 0;
```

### 3. 查看候选人技能匹配度
```sql
SELECT
    CONCAT(c.first_name, ' ', c.last_name) as candidate_name,
    s.skill_name,
    cs.proficiency_level,
    cs.years_experience
FROM candidates c
JOIN candidate_skills cs ON c.candidate_id = cs.candidate_id
JOIN skills s ON cs.skill_id = s.skill_id
WHERE c.candidate_code = 'CAND001'
ORDER BY s.category, cs.proficiency_level;
```

### 4. 查看面试评价统计
```sql
SELECT
    CONCAT(c.first_name, ' ', c.last_name) as candidate_name,
    COUNT(ie.evaluation_id) as interview_count,
    AVG(ie.overall_score) as avg_score,
    MAX(ie.overall_score) as max_score,
    MIN(ie.overall_score) as min_score
FROM candidates c
JOIN job_applications ja ON c.candidate_id = ja.candidate_id
JOIN interviews i ON ja.application_id = i.application_id
JOIN interview_evaluations ie ON i.interview_id = ie.interview_id
WHERE c.status = 'interviewing'
GROUP BY c.candidate_id, c.first_name, c.last_name
ORDER BY avg_score DESC;
```

### 5. 查找推荐录用的候选人
```sql
SELECT DISTINCT
    CONCAT(c.first_name, ' ', c.last_name) as candidate_name,
    p.position_title,
    COUNT(ie.evaluation_id) as evaluation_count
FROM candidates c
JOIN job_applications ja ON c.candidate_id = ja.candidate_id
JOIN positions p ON ja.position_id = p.position_id
JOIN interviews i ON ja.application_id = i.application_id
JOIN interview_evaluations ie ON i.interview_id = ie.interview_id
WHERE ie.recommendation IN ('strong_hire', 'hire')
GROUP BY c.candidate_id, c.first_name, c.last_name, p.position_title
HAVING COUNT(ie.evaluation_id) >= 3
ORDER BY evaluation_count DESC;
```

### 6. 查看面试官工作负载
```sql
SELECT
    CONCAT(e.first_name, ' ', e.last_name) as interviewer_name,
    d.department_name,
    COUNT(DISTINCT ip.interview_id) as total_interviews,
    COUNT(DISTINCT ie.evaluation_id) as evaluations_completed
FROM employees e
JOIN departments d ON e.department_id = d.department_id
LEFT JOIN interview_participants ip ON e.employee_id = ip.employee_id
LEFT JOIN interview_evaluations ie ON e.employee_id = ie.employee_id
GROUP BY e.employee_id, e.first_name, e.last_name, d.department_name
ORDER BY total_interviews DESC;
```

### 7. 查看候选人来源统计
```sql
SELECT
    source,
    COUNT(*) as candidate_count,
    SUM(CASE WHEN status = 'hired' THEN 1 ELSE 0 END) as hired,
    SUM(CASE WHEN status = 'interviewing' THEN 1 ELSE 0 END) as interviewing,
    SUM(CASE WHEN status = 'offered' THEN 1 ELSE 0 END) as offered,
    ROUND(SUM(CASE WHEN status = 'hired' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as hire_rate
FROM candidates
GROUP BY source
ORDER BY candidate_count DESC;
```

### 8. 查看各阶段面试通过率
```sql
SELECT
    s.stage_name,
    COUNT(i.interview_id) as total_interviews,
    SUM(CASE WHEN i.status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN i.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
    ROUND(SUM(CASE WHEN i.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(i.interview_id), 2) as completion_rate
FROM interviews i
JOIN interview_stages s ON i.stage_id = s.stage_id
GROUP BY s.stage_id, s.stage_name
ORDER BY s.stage_order;
```

## 🎯 典型使用场景

### 场景 1: 安排新面试
```sql
-- 1. 查找可用的面试官
SELECT employee_id, CONCAT(first_name, ' ', last_name) as name
FROM employees
WHERE department_id = 1 AND status = 'active';

-- 2. 创建面试安排
INSERT INTO interviews (application_id, stage_id, scheduled_date, duration_minutes, location, status)
VALUES (15, 3, '2024-02-10 14:00:00', 60, 'Meeting Room A', 'scheduled');

-- 3. 添加面试参与者
INSERT INTO interview_participants (interview_id, employee_id, role)
VALUES (LAST_INSERT_ID(), 1, 'lead_interviewer');
```

### 场景 2: 提交面试评价
```sql
INSERT INTO interview_evaluations
(interview_id, employee_id, technical_score, communication_score,
 problem_solving_score, cultural_fit_score, overall_score, recommendation,
 strengths, weaknesses, additional_notes)
VALUES
(20, 1, 5, 4, 5, 4, 5, 'strong_hire',
 'Excellent technical skills', 'None', 'Strong candidate');
```

### 场景 3: 发送录用通知
```sql
INSERT INTO offers
(application_id, offer_date, salary_offered, signing_bonus, start_date, status, expiry_date)
VALUES
(12, '2024-02-15', 180000.00, 15000.00, '2024-03-15', 'pending', '2024-03-01');

-- 更新候选人状态
UPDATE job_applications SET status = 'offered' WHERE application_id = 12;
UPDATE candidates SET status = 'offered' WHERE candidate_id = 12;
```

## 📊 数据统计

### 基础数据
- **8 个部门**: Engineering, Product, Design, Marketing, Sales, HR, Finance, Operations
- **10 个职位**: 涵盖开发、产品、设计、市场、销售、HR 等岗位
- **30+ 种技能**: 技术、软技能、语言、工具四大类
- **15 名候选人**: 处于不同招聘阶段
- **19 场面试**: 包含多个面试阶段
- **13 条评价**: 多维度评分和推荐意见

### 候选人状态分布
- **Interviewing**: 10 名候选人
- **Screening**: 1 名候选人
- **Offered**: 1 名候选人
- **Applied**: 2 名候选人

### 职位申请情况
- **Senior Software Engineer**: 4 个申请
- **Full Stack Developer**: 3 个申请
- **DevOps Engineer**: 2 个申请
- **ML Engineer**: 1 个申请
- **Data Engineer**: 1 个申请
- **UI/UX Designer**: 2 个申请
- 其他职位各有申请

## 🔍 索引优化

数据库已在关键字段上创建索引：
- 外键字段
- 查询频繁的字段 (email, status, code 等)
- 日期字段 (application_date, scheduled_date, offer_date)
- 唯一约束 (candidate_code, employee_code, email 等)

## 🛡️ 数据完整性

- 外键约束确保引用完整性
- CHECK 约束确保分数在有效范围内 (1-5)
- UNIQUE 约束确保数据唯一性
- NOT NULL 约束确保必填字段
- ON DELETE CASCADE/RESTRICT 维护数据关系

## 📈 扩展建议

可以考虑添加的功能：
1. 面试反馈自动汇总
2. 候选人画像分析
3. 招聘漏斗分析
4. 面试官评价偏差分析
5. 薪资范围分析
6. 招聘周期统计
7. Offer 接受率分析
8. 技能需求趋势分析

## 📞 联系信息

数据库版本: 1.0
创建日期: 2024-02-06
最后更新: 2024-02-06
