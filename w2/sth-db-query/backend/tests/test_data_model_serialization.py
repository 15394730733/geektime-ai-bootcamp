"""
Property-based tests for data model serialization.

Feature: database-query-tool, Property 7: Query result formatting
**Validates: Requirements 3.5, 9.7**
"""

import json
from datetime import datetime
from hypothesis import given, strategies as st, settings
import pytest

from app.schemas.database import Database, ColumnMetadata, TableMetadata, DatabaseMetadata
from app.schemas.query import QueryResult, NaturalLanguageQueryResult


class TestDataModelSerialization:
    """Property-based tests for data model serialization functionality."""

    @given(
        columns=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc"), min_codepoint=32, max_codepoint=126), min_size=1, max_size=20),
            min_size=1,
            max_size=10
        ),
        row_count=st.integers(min_value=0, max_value=1000),
        execution_time=st.integers(min_value=1, max_value=30000),
        truncated=st.booleans()
    )
    @settings(max_examples=5, deadline=10000)
    def test_query_result_camel_case_serialization(self, columns, row_count, execution_time, truncated):
        """
        Property 7: Query result formatting
        
        For any query result data, serialization should produce JSON with camelCase field names
        and all data should be preserved during serialization/deserialization.
        
        **Validates: Requirements 3.5, 9.7**
        """
        # Generate sample rows based on columns
        rows = []
        for _ in range(min(row_count, 5)):  # Limit to 5 rows for performance
            row = []
            for col in columns:
                # Generate simple test data
                row.append(f"value_{len(row)}")
            rows.append(row)
        
        # Create QueryResult instance
        result = QueryResult(
            columns=columns,
            rows=rows,
            row_count=row_count,
            execution_time_ms=execution_time,
            truncated=truncated
        )
        
        # Serialize to JSON with camelCase aliases
        json_data = result.model_dump(by_alias=True)
        
        # Verify camelCase field names are used
        assert "rowCount" in json_data
        assert "executionTimeMs" in json_data
        assert "row_count" not in json_data
        assert "execution_time_ms" not in json_data
        
        # Verify all data is preserved
        assert json_data["columns"] == columns
        assert json_data["rows"] == rows
        assert json_data["rowCount"] == row_count
        assert json_data["executionTimeMs"] == execution_time
        assert json_data["truncated"] == truncated
        
        # Verify JSON serialization works
        json_str = json.dumps(json_data, default=str)
        assert isinstance(json_str, str)
        
        # Verify deserialization works
        parsed_data = json.loads(json_str)
        assert parsed_data["rowCount"] == row_count
        assert parsed_data["executionTimeMs"] == execution_time

    @given(
        generated_sql=st.text(min_size=1, max_size=200),
        columns=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc"), min_codepoint=32, max_codepoint=126), min_size=1, max_size=20),
            min_size=1,
            max_size=5
        ),
        row_count=st.integers(min_value=0, max_value=100),
        execution_time=st.integers(min_value=1, max_value=10000),
        truncated=st.booleans()
    )
    @settings(max_examples=5, deadline=10000)
    def test_natural_language_result_camel_case_serialization(self, generated_sql, columns, row_count, execution_time, truncated):
        """
        Property 7: Query result formatting - Natural Language Results
        
        For any natural language query result, serialization should produce JSON with camelCase 
        field names and preserve all data.
        
        **Validates: Requirements 3.5, 9.7**
        """
        # Generate sample rows
        rows = []
        for _ in range(min(row_count, 3)):  # Limit for performance
            row = [f"val_{i}" for i in range(len(columns))]
            rows.append(row)
        
        # Create NaturalLanguageQueryResult instance
        result = NaturalLanguageQueryResult(
            generated_sql=generated_sql,
            columns=columns,
            rows=rows,
            row_count=row_count,
            execution_time_ms=execution_time,
            truncated=truncated
        )
        
        # Serialize to JSON with camelCase aliases
        json_data = result.model_dump(by_alias=True)
        
        # Verify camelCase field names are used
        assert "generatedSql" in json_data
        assert "rowCount" in json_data
        assert "executionTimeMs" in json_data
        assert "generated_sql" not in json_data
        assert "row_count" not in json_data
        assert "execution_time_ms" not in json_data
        
        # Verify all data is preserved
        assert json_data["generatedSql"] == generated_sql
        assert json_data["columns"] == columns
        assert json_data["rows"] == rows
        assert json_data["rowCount"] == row_count
        assert json_data["executionTimeMs"] == execution_time
        assert json_data["truncated"] == truncated

    @given(
        name=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc"), min_codepoint=32, max_codepoint=126), min_size=1, max_size=30),
        data_type=st.sampled_from(["integer", "varchar", "text", "boolean", "timestamp", "numeric"]),
        is_nullable=st.booleans(),
        is_primary_key=st.booleans(),
        default_value=st.one_of(st.none(), st.text(min_size=0, max_size=50))
    )
    @settings(max_examples=5, deadline=10000)
    def test_column_metadata_camel_case_serialization(self, name, data_type, is_nullable, is_primary_key, default_value):
        """
        Property 7: Query result formatting - Column Metadata
        
        For any column metadata, serialization should produce JSON with camelCase field names
        and preserve all data accurately.
        
        **Validates: Requirements 3.5, 9.7**
        """
        # Create ColumnMetadata instance
        column = ColumnMetadata(
            name=name,
            data_type=data_type,
            is_nullable=is_nullable,
            is_primary_key=is_primary_key,
            default_value=default_value
        )
        
        # Serialize to JSON with camelCase aliases
        json_data = column.model_dump(by_alias=True)
        
        # Verify camelCase field names are used
        assert "dataType" in json_data
        assert "isNullable" in json_data
        assert "isPrimaryKey" in json_data
        assert "defaultValue" in json_data
        assert "data_type" not in json_data
        assert "is_nullable" not in json_data
        assert "is_primary_key" not in json_data
        assert "default_value" not in json_data
        
        # Verify all data is preserved
        assert json_data["name"] == name
        assert json_data["dataType"] == data_type
        assert json_data["isNullable"] == is_nullable
        assert json_data["isPrimaryKey"] == is_primary_key
        assert json_data["defaultValue"] == default_value

    @given(
        db_name=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc"), min_codepoint=32, max_codepoint=126), min_size=1, max_size=30),
        url=st.just("postgresql://user:pass@localhost:5432/testdb"),  # Use fixed valid URL
        description=st.one_of(st.none(), st.text(min_size=0, max_size=100)),
        is_active=st.booleans()
    )
    @settings(max_examples=5, deadline=10000)
    def test_database_camel_case_serialization(self, db_name, url, description, is_active):
        """
        Property 7: Query result formatting - Database Model
        
        For any database connection data, serialization should produce JSON with camelCase 
        field names and preserve all data accurately.
        
        **Validates: Requirements 3.5, 9.7**
        """
        # Filter out invalid characters for database names
        clean_name = ''.join(c for c in db_name if c.isalnum() or c in ['_', '-'])
        if not clean_name:
            clean_name = "test_db"
        
        # Create Database instance
        now = datetime.now()
        database = Database(
            id="test-id",
            name=clean_name,
            url=url,
            description=description,
            created_at=now,
            updated_at=now,
            is_active=is_active
        )
        
        # Serialize to JSON with camelCase aliases
        json_data = database.model_dump(by_alias=True)
        
        # Verify camelCase field names are used
        assert "createdAt" in json_data
        assert "updatedAt" in json_data
        assert "isActive" in json_data
        assert "created_at" not in json_data
        assert "updated_at" not in json_data
        assert "is_active" not in json_data
        
        # Verify all data is preserved
        assert json_data["name"] == clean_name
        assert json_data["url"] == url
        assert json_data["description"] == description
        assert json_data["isActive"] == is_active

    @given(
        table_name=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc"), min_codepoint=32, max_codepoint=126), min_size=1, max_size=30),
        schema_name=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc"), min_codepoint=32, max_codepoint=126), min_size=1, max_size=20),
        column_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=5, deadline=10000)
    def test_table_metadata_camel_case_serialization(self, table_name, schema_name, column_count):
        """
        Property 7: Query result formatting - Table Metadata
        
        For any table metadata, serialization should produce JSON with camelCase field names
        and preserve nested column data accurately.
        
        **Validates: Requirements 3.5, 9.7**
        """
        # Create sample columns
        columns = []
        for i in range(column_count):
            column = ColumnMetadata(
                name=f"col_{i}",
                data_type="varchar",
                is_nullable=True,
                is_primary_key=(i == 0),
                default_value=None
            )
            columns.append(column)
        
        # Create TableMetadata instance
        table = TableMetadata(
            name=table_name,
            db_schema=schema_name,
            columns=columns
        )
        
        # Serialize to JSON with camelCase aliases
        json_data = table.model_dump(by_alias=True)
        
        # Verify table data is preserved
        assert json_data["name"] == table_name
        assert json_data["schema"] == schema_name
        assert len(json_data["columns"]) == column_count
        
        # Verify nested column data uses camelCase
        for i, col_data in enumerate(json_data["columns"]):
            assert "dataType" in col_data
            assert "isNullable" in col_data
            assert "isPrimaryKey" in col_data
            assert "defaultValue" in col_data
            assert col_data["name"] == f"col_{i}"
            assert col_data["dataType"] == "varchar"
