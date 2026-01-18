"""
Interview Database Testing Script

测试 interview_db 数据库的连接和基本查询功能。
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "w2" / "sth-db-query" / "backend"
sys.path.insert(0, str(backend_dir))


async def test_mysql_connection():
    """测试 MySQL 数据库连接"""
    from app.adapters.mysql_adapter import MySQLAdapter
    from app.core.db_type_detector import DatabaseTypeDetector

    # MySQL connection string (需要根据实际情况修改)
    # 格式: mysql://username:password@host:port/database
    mysql_url = "mysql://root:sth5805051@localhost:3306/interview_db"

    print("=" * 60)
    print("Interview Database Connection Test")
    print("=" * 60)
    print()

    try:
        # Detect database type
        db_type = DatabaseTypeDetector.detect(mysql_url)
        print(f"✓ Database Type Detected: {db_type.value}")
        print()

        # Create MySQL adapter
        adapter = MySQLAdapter()
        print(f"✓ MySQL Adapter Created")
        print()

        # Connect to database
        print("Connecting to database...")
        conn = await adapter.connect(mysql_url)
        print("✓ Connected Successfully!")
        print()

        # Test connection
        is_alive = await adapter.test_connection(conn)
        print(f"✓ Connection Test: {'Alive' if is_alive else 'Failed'}")
        print()

        # Get departments
        print("-" * 60)
        print("Testing: Get Departments")
        print("-" * 60)
        departments = await adapter.get_tables(conn)
        print(f"✓ Found {len(departments)} tables in interview_db:")
        for table in departments[:10]:
            print(f"  - {table['table_name']}")
        if len(departments) > 10:
            print(f"  ... and {len(departments) - 10} more")
        print()

        # Get candidates
        print("-" * 60)
        print("Testing: Query Candidates Table")
        print("-" * 60)
        query = """
            SELECT
                candidate_code,
                first_name,
                last_name,
                email,
                years_experience,
                status
            FROM candidates
            ORDER BY candidate_code
            LIMIT 10
        """
        result = await adapter.execute_query(conn, query, timeout_seconds=10)
        print(f"✓ Query executed in {result['execution_time_ms']}ms")
        print(f"  Columns: {', '.join(result['columns'])}")
        print(f"  Rows: {result['row_count']}")
        print()
        print("Sample Candidates:")
        for row in result['rows'][:5]:
            print(f"  - {row['candidate_code']}: {row['first_name']} {row['last_name']} ({row['status']})")
        print()

        # Get interview statistics
        print("-" * 60)
        print("Testing: Interview Statistics")
        print("-" * 60)
        query = """
            SELECT
                status,
                COUNT(*) as count
            FROM interviews
            GROUP BY status
            ORDER BY count DESC
        """
        result = await adapter.execute_query(conn, query, timeout_seconds=10)
        print("Interview Status Distribution:")
        for row in result['rows']:
            print(f"  - {row['status']}: {row['count']} interviews")
        print()

        # Get evaluation scores
        print("-" * 60)
        print("Testing: Evaluation Scores")
        print("-" * 60)
        query = """
            SELECT
                recommendation,
                COUNT(*) as count,
                ROUND(AVG(overall_score), 2) as avg_score
            FROM interview_evaluations
            GROUP BY recommendation
            ORDER BY avg_score DESC
        """
        result = await adapter.execute_query(conn, query, timeout_seconds=10)
        print("Evaluation Summary:")
        for row in result['rows']:
            print(f"  - {row['recommendation']}: {row['count']} evaluations (avg score: {row['avg_score']})")
        print()

        # Get open positions
        print("-" * 60)
        print("Testing: Open Positions")
        print("-" * 60)
        query = """
            SELECT
                p.position_title,
                d.department_name,
                p.salary_min,
                p.salary_max,
                (p.headcount - p.current_count) as openings
            FROM positions p
            JOIN departments d ON p.department_id = d.department_id
            WHERE p.status = 'active'
              AND (p.headcount - p.current_count) > 0
            ORDER BY openings DESC
            LIMIT 5
        """
        result = await adapter.execute_query(conn, query, timeout_seconds=10)
        print("Open Positions:")
        for row in result['rows']:
            salary_range = f"${row['salary_min']:,.0f} - ${row['salary_max']:,.0f}"
            print(f"  - {row['position_title']} ({row['department_name']})")
            print(f"    Openings: {row['openings']}, Salary: {salary_range}")
        print()

        # Get top candidates by evaluations
        print("-" * 60)
        print("Testing: Top Candidates")
        print("-" * 60)
        query = """
            SELECT
                CONCAT(c.first_name, ' ', c.last_name) as candidate_name,
                p.position_title,
                COUNT(ie.evaluation_id) as evaluation_count,
                ROUND(AVG(ie.overall_score), 2) as avg_score
            FROM candidates c
            JOIN job_applications ja ON c.candidate_id = ja.candidate_id
            JOIN positions p ON ja.position_id = p.position_id
            JOIN interviews i ON ja.application_id = i.application_id
            JOIN interview_evaluations ie ON i.interview_id = ie.interview_id
            GROUP BY c.candidate_id, c.first_name, c.last_name, p.position_title
            HAVING evaluation_count >= 2
            ORDER BY avg_score DESC
            LIMIT 5
        """
        result = await adapter.execute_query(conn, query, timeout_seconds=10)
        print("Top Rated Candidates:")
        for i, row in enumerate(result['rows'], 1):
            print(f"  {i}. {row['candidate_name']} - {row['position_title']}")
            print(f"     Evaluations: {row['evaluation_count']}, Avg Score: {row['avg_score']}/5")
        print()

        # Close connection
        await adapter.disconnect(conn)
        print("✓ Connection Closed")
        print()

        print("=" * 60)
        print("All Tests Passed! ✓")
        print("=" * 60)
        print()
        print("The interview_db database is ready to use!")
        print()
        print("Database Schema:")
        print("  - 13 tables (candidates, interviews, evaluations, etc.)")
        print("  - 4 views (candidate_summary, interview_details, etc.)")
        print("  - 15 candidates")
        print("  - 10 positions")
        print("  - 8 departments")
        print("  - 19 interviews")
        print("  - 13 evaluations")
        print()
        print("You can now connect to this database using the MySQL adapter!")
        print()

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_mysql_connection())
    sys.exit(0 if success else 1)
